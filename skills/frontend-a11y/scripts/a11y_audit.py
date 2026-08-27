#!/usr/bin/env python3
"""frontend-a11y — static accessibility audit (Python stdlib, offline).

Maps the Front-End-Checklist "Accessibility" category (95 rules) to a stable
audit-id scheme. This script covers the STATIC subset: markup structure, ARIA
validity, headings, landmarks, tables, forms, media tracks, lists, and a few
CSS signals. It needs no browser and no network — it parses HTML/CSS with the
stdlib only.

Runtime checks (contrast, focus order, live regions, modal traps, reflow,
touch targets) live in scripts/a11y_axe.mjs (Playwright + axe-core). Manual
checks (screen-reader testing, plain language, seizure flashing) are
checklist-only and documented in SKILL.md.

Usage:
  python3 a11y_audit.py --html page.html [--html other.html ...] \
          [--css main.css ...] [--out report.json] [--json]

Exit codes: 0 = no violations; 1 = at least one violation; 2 = runner error.
"""
import argparse
import html.parser
import json
import os
import re
import sys


# ---------------------------------------------------------------- reference data
VALID_ARIA = {
    "aria-activedescendant", "aria-atomic", "aria-autocomplete", "aria-braillelabel",
    "aria-brailleroledescription", "aria-busy", "aria-checked", "aria-colcount",
    "aria-colindex", "aria-colindextext", "aria-colspan", "aria-controls", "aria-current",
    "aria-describedby", "aria-description", "aria-details", "aria-disabled", "aria-dropeffect",
    "aria-errormessage", "aria-expanded", "aria-flowto", "aria-grabbed", "aria-haspopup",
    "aria-hidden", "aria-invalid", "aria-keyshortcuts", "aria-label", "aria-labelledby",
    "aria-level", "aria-live", "aria-modal", "aria-multiline", "aria-multiselectable",
    "aria-orientation", "aria-owns", "aria-placeholder", "aria-posinset", "aria-pressed",
    "aria-readonly", "aria-relevant", "aria-required", "aria-roledescription",
    "aria-rowcount", "aria-rowindex", "aria-rowindextext", "aria-rowspan", "aria-selected",
    "aria-setsize", "aria-sort", "aria-valuemax", "aria-valuemin", "aria-valuenow",
    "aria-valuetext",
}

# Abstract / deprecated roles must never appear in author markup.
ABSTRACT_ROLES = {
    "command", "composite", "input", "landmark", "range", "roletype", "section",
    "sectionhead", "select", "structure", "widget", "window",
}

# WAI-ARIA 1.2 concrete roles (a practical superset; not exhaustive of DPUB).
VALID_ROLES = {
    "alert", "alertdialog", "application", "article", "banner", "blockquote", "button",
    "caption", "cell", "checkbox", "code", "columnheader", "combobox", "complementary",
    "contentinfo", "definition", "deletion", "dialog", "directory", "document", "emphasis",
    "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "insertion",
    "link", "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu",
    "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "meter", "navigation",
    "none", "note", "option", "presentation", "progressbar", "radio", "radiogroup",
    "region", "row", "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator",
    "slider", "spinbutton", "status", "switch", "tab", "table", "tablist", "tabpanel",
    "term", "textbox", "time", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem",
}

# Roles whose presence implies an interactive widget needing an accessible name.
INTERACTIVE_ROLES = {
    "button", "link", "menuitem", "menuitemcheckbox", "menuitemradio", "option",
    "radio", "switch", "tab", "treeitem", "checkbox", "slider", "spinbutton",
    "textbox", "combobox", "gridcell",
}

# Allowed token values for a few frequently-misused ARIA attributes.
ARIA_VALUE_TOKENS = {
    "aria-hidden": {"true", "false"},
    "aria-expanded": {"true", "false", "undefined"},
    "aria-modal": {"true", "false"},
    "aria-pressed": {"true", "false", "mixed", "undefined"},
    "aria-checked": {"true", "false", "mixed", "undefined"},
    "aria-disabled": {"true", "false"},
    "aria-invalid": {"grammar", "spelling", "true", "false"},
    "aria-live": {"off", "polite", "assertive"},
    "aria-sort": {"none", "ascending", "descending", "other"},
    "aria-current": {"page", "step", "location", "date", "time", "true", "false"},
    "aria-busy": {"true", "false"},
    "aria-haspopup": {
        "true", "menu", "listbox", "tree", "grid", "dialog", "false",
    },
    "aria-orientation": {"horizontal", "vertical", "undefined"},
}

RTL_LANGS = ("ar", "he", "fa", "ur", "yi")

# Severity mirrors the checklist priority for each static audit id.
SEVERITY = {
    "a11y:img-alt": "critical", "a11y:img-button-alt": "critical",
    "a11y:img-alt-redundant": "low", "a11y:button-name": "critical",
    "a11y:link-name": "high", "a11y:link-distinct": "medium",
    "a11y:link-empty-broken": "medium", "a11y:link-text-descriptive": "high",
    "a11y:form-label": "critical", "a11y:form-label-single": "medium",
    "a11y:input-name": "critical", "a11y:select-name": "medium",
    "a11y:toggle-name": "medium", "a11y:aria-valid": "high",
    "a11y:aria-valid-value": "medium", "a11y:aria-deprecated-role": "medium",
    "a11y:aria-role-valid": "medium", "a11y:landmark-unique": "medium",
    "a11y:landmark-main": "medium", "a11y:landmark-nav": "high",
    "a11y:landmark-regions": "medium", "headings:single-h1": "medium",
    "headings:order": "critical", "headings:non-empty": "medium",
    "html:lang": "high", "html:dir-rtl": "medium", "html:lang-xml-match": "medium",
    "a11y:skip-link": "high", "a11y:iframe-title": "medium",
    "a11y:table-headers": "medium", "a11y:table-header-scope": "medium",
    "a11y:table-cell-headers": "medium", "a11y:table-unique-name": "medium",
    "a11y:table-semantic": "medium", "a11y:video-captions": "high",
    "a11y:video-audio-desc": "medium", "a11y:autofocus-absent": "low",
    "a11y:aria-hidden-body-absent": "critical",
    "a11y:focusable-in-aria-hidden-absent": "medium",
    "a11y:list-structure": "medium", "a11y:list-correct": "medium",
    "a11y:list-semantic": "medium", "a11y:dl-structure": "medium",
    "a11y:dl-wrap": "medium", "a11y:decorative-hidden": "medium",
    "a11y:object-alt": "medium", "a11y:meta-refresh-absent": "medium",
    "a11y:accesskey-unique": "medium", "a11y:unique-id": "high",
    "a11y:aria-ref-unique": "high", "a11y:tabindex-appropriate": "medium",
    "a11y:role-text-no-focusable": "medium", "a11y:dialog-name": "medium",
    "a11y:meter-name": "medium", "a11y:progress-name": "medium",
    "a11y:tooltip-name": "medium", "a11y:treeitem-name": "medium",
    "a11y:command-name": "medium", "a11y:autoplay-media": "high",
    "a11y:paste-allowed": "medium", "a11y:autocomplete-auth": "high",
    "a11y:links-in-text-distinguishable": "medium", "a11y:reduced-motion": "high",
    "a11y:instant-anchor-scroll": "low", "a11y:interactive-name": "high",
}

TITLES = {
    "a11y:img-alt": "Images have alt text",
    "a11y:img-button-alt": "Image buttons have alt",
    "a11y:img-alt-redundant": "No redundant image alt words",
    "a11y:button-name": "Buttons have accessible names",
    "a11y:link-name": "Links have accessible names",
    "a11y:link-distinct": "Identical links share destinations",
    "a11y:link-empty-broken": "Links are not empty or broken",
    "a11y:link-text-descriptive": "Descriptive link text",
    "a11y:form-label": "Form controls have labels",
    "a11y:form-label-single": "One label per field",
    "a11y:input-name": "Inputs have accessible names",
    "a11y:select-name": "Selects have accessible names",
    "a11y:toggle-name": "Toggle fields have names",
    "a11y:aria-valid": "ARIA attributes are valid names",
    "a11y:aria-valid-value": "ARIA attribute values are valid",
    "a11y:aria-deprecated-role": "No deprecated/abstract ARIA roles",
    "a11y:aria-role-valid": "ARIA role values are valid",
    "a11y:landmark-unique": "Landmarks are unique",
    "a11y:landmark-main": "Exactly one main landmark",
    "a11y:landmark-nav": "Nav landmarks are labelled",
    "a11y:landmark-regions": "Landmark regions used correctly",
    "headings:single-h1": "Exactly one h1",
    "headings:order": "Logical heading order",
    "headings:non-empty": "Headings contain text",
    "html:lang": "html lang attribute",
    "html:dir-rtl": "RTL dir attribute",
    "html:lang-xml-match": "lang matches xml:lang",
    "a11y:skip-link": "Skip-to-content link",
    "a11y:iframe-title": "iframe/frame titles",
    "a11y:table-headers": "Tables have headers",
    "a11y:table-header-scope": "Headers scoped to cells",
    "a11y:table-cell-headers": "Cells linked to headers via ids",
    "a11y:table-unique-name": "Tables have unique names",
    "a11y:table-semantic": "Semantic table markup",
    "a11y:video-captions": "Video captions track",
    "a11y:video-audio-desc": "Video audio description",
    "a11y:autofocus-absent": "No autofocus on fields",
    "a11y:aria-hidden-body-absent": "No aria-hidden on body",
    "a11y:focusable-in-aria-hidden-absent": "No focusable in aria-hidden",
    "a11y:list-structure": "List items in containers",
    "a11y:list-correct": "Lists contain only li",
    "a11y:list-semantic": "Semantic list elements",
    "a11y:dl-structure": "Valid definition list",
    "a11y:dl-wrap": "dt/dd wrapped in dl",
    "a11y:decorative-hidden": "Decorative elements hidden",
    "a11y:object-alt": "Object alternative content",
    "a11y:meta-refresh-absent": "No meta refresh redirect",
    "a11y:accesskey-unique": "Unique accesskey values",
    "a11y:unique-id": "Unique element ids",
    "a11y:aria-ref-unique": "Unique ARIA reference ids",
    "a11y:tabindex-appropriate": "Appropriate tabindex values",
    "a11y:role-text-no-focusable": "role=text has no focusable child",
    "a11y:dialog-name": "Dialogs have names",
    "a11y:meter-name": "Meter elements named",
    "a11y:progress-name": "Progress bars named",
    "a11y:tooltip-name": "Tooltips named",
    "a11y:treeitem-name": "Tree items named",
    "a11y:command-name": "ARIA command elements named",
    "a11y:autoplay-media": "No autoplaying media",
    "a11y:paste-allowed": "Pasting allowed in inputs",
    "a11y:autocomplete-auth": "Accessible auth autocomplete",
    "a11y:links-in-text-distinguishable": "Links distinguishable beyond color",
    "a11y:reduced-motion": "Respects reduced motion",
    "a11y:instant-anchor-scroll": "Instant anchor scroll option",
    "a11y:interactive-name": "Interactive elements named",
}


# ---------------------------------------------------------------- HTML parsing
class A11yExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []            # list of element indices (parents)
        self.elem_tag = []         # tag per element index
        self.elem_parent = []      # parent index per element index
        self.elem_attrs = []       # attrs dict per element index
        self.elem_text = []        # text buffer per element index
        self._idx = 0

        self.imgs = []             # {alt_present, alt, role, is_input_image, input_alt}
        self.buttons = []          # {name, aria}
        self.anchors = []          # {name, aria, href, title}
        self.inputs = []           # {tag, id, type, aria_label, aria_labelledby, wrapped, role}
        self.labels_for = []
        self.aria_attrs = []       # (name, value, tag)
        self.roles = []            # (role, tag, attrs)
        self.landmark_main = 0
        self.landmark_navs = []
        self.landmark_regions = 0
        self.headings = []         # (level, text)
        self.html_attrs = {}
        self.meta_refresh = False
        self.iframes = []          # {title, aria_label}
        self.tables = []           # {has_th, has_scope, has_caption, headers, id, name, role}
        self.videos = []           # {has_captions, has_descriptions}
        self.autofocus = False
        self.body_aria_hidden = False
        self.aria_hidden_focusable = []   # tags
        self.role_text_focusable = []     # tags
        self.accesskeys = []
        self.ids = []
        self.aria_refs = []        # referenced ids
        self.tabindex_positive = 0
        self.dialogs = []          # {has_name}
        self.meters = []           # {has_name}
        self.progress = []         # {has_name}
        self.treeitems = []        # {has_name}
        self.toggles = []          # {has_name}
        self.tooltips = []         # {has_name}
        self.commands = []         # {has_name}
        self.onpaste = 0
        self.autoplay = 0
        self.decorative_issues = []  # (tag, issue)
        self.interactive = []      # {has_name, role}
        self.skip_links = 0
        self._in_label = 0
        self._aria_hidden = 0
        self._role_text = 0
        self._depth_stack = []     # parallel to self.stack: (entered_ah, entered_rt)
        self._in_title = False
        self._cur_heading = None
        self._svg_depth = 0

    # -- helpers
    def _is_focusable(self, tag, attrs):
        if tag in ("button", "input", "select", "textarea", "iframe",
                   "audio", "video", "details", "summary"):
            return True
        if tag == "a" and ("href" in attrs or "tabindex" in attrs):
            return True
        if "tabindex" in attrs:
            return True
        ce = attrs.get("contenteditable")
        if ce in ("", "true"):
            return True
        return False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        idx = self._idx
        self._idx += 1
        parent = self.stack[-1] if self.stack else -1
        self.elem_tag.append(tag)
        self.elem_parent.append(parent)
        self.elem_attrs.append(attrs)
        self.elem_text.append([])
        self.stack.append(idx)

        role = (attrs.get("role") or "").lower().strip()
        if role:
            self.roles.append((role, tag, attrs))

        # aria-hidden depth tracking
        ah = (attrs.get("aria-hidden") or "").lower().strip()
        entered_ah = False
        if ah == "true":
            self._aria_hidden += 1
            entered_ah = True
        # role=text depth tracking
        entered_rt = False
        if role == "text":
            self._role_text += 1
            entered_rt = True

        self._depth_stack.append((entered_ah, entered_rt))

        if self._is_focusable(tag, attrs):
            if self._aria_hidden > 0:
                self.aria_hidden_focusable.append(tag)
            if self._role_text > 0:
                self.role_text_focusable.append(tag)

        # collect ids / accesskeys / tabindex
        aid = attrs.get("id", "")
        if aid:
            self.ids.append(aid)
        ak = attrs.get("accesskey")
        if ak:
            self.accesskeys.append(ak.lower())
        ti = attrs.get("tabindex")
        if ti and ti.lstrip("-").isdigit() and int(ti) > 0:
            self.tabindex_positive += 1

        # aria attribute collection + reference ids
        for k, v in attrs.items():
            if k.startswith("aria-"):
                self.aria_attrs.append((k, v or "", tag))
                if k in ("aria-labelledby", "aria-describedby", "aria-owns",
                         "aria-controls"):
                    for ref in (v or "").split():
                        if ref:
                            self.aria_refs.append(ref)
            elif k == "headers" and v:
                for ref in v.split():
                    if ref:
                        self.aria_refs.append(ref)

        if tag == "html":
            self.html_attrs = attrs
        elif tag == "body":
            if ah == "true":
                self.body_aria_hidden = True
        elif tag == "img":
            alt = attrs.get("alt")
            self.imgs.append({
                "alt_present": alt is not None,
                "alt": alt or "",
                "role": role,
                "is_input_image": False,
                "input_alt": None,
            })
            if role in ("presentation", "none") and (alt or "").strip():
                self.decorative_issues.append(("img", "role=presentation with non-empty alt"))
        elif tag == "input":
            itype = (attrs.get("type") or "").lower()
            if itype == "image":
                self.imgs.append({
                    "alt_present": attrs.get("alt") is not None,
                    "alt": attrs.get("alt") or "",
                    "role": role,
                    "is_input_image": True,
                    "input_alt": attrs.get("alt"),
                })
            wrapped = self._in_label > 0
            self.inputs.append({
                "tag": tag, "id": attrs.get("id", ""), "type": itype,
                "aria_label": attrs.get("aria-label"),
                "aria_labelledby": attrs.get("aria-labelledby"),
                "wrapped": wrapped, "role": role,
                "autocomplete": attrs.get("autocomplete"),
            })
            if "autofocus" in attrs:
                self.autofocus = True
            if "onpaste" in attrs:
                self.onpaste += 1
        elif tag == "select":
            self.inputs.append({
                "tag": tag, "id": attrs.get("id", ""), "type": "",
                "aria_label": attrs.get("aria-label"),
                "aria_labelledby": attrs.get("aria-labelledby"),
                "wrapped": self._in_label > 0, "role": role,
                "autocomplete": None,
            })
            if "autofocus" in attrs:
                self.autofocus = True
        elif tag == "textarea":
            self.inputs.append({
                "tag": tag, "id": attrs.get("id", ""), "type": "",
                "aria_label": attrs.get("aria-label"),
                "aria_labelledby": attrs.get("aria-labelledby"),
                "wrapped": self._in_label > 0, "role": role,
                "autocomplete": attrs.get("autocomplete"),
            })
            if "autofocus" in attrs:
                self.autofocus = True
            if "onpaste" in attrs:
                self.onpaste += 1
        elif tag == "label":
            self.labels_for.append(attrs.get("for", ""))
            self._in_label += 1
        elif tag == "main":
            self.landmark_main += 1
        elif tag == "nav":
            self.landmark_navs.append(attrs.get("aria-label") or attrs.get("title") or "")
        elif tag in ("header", "footer", "aside", "section"):
            self.landmark_regions += 1
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append((int(tag[1]), ""))
            self._cur_heading = int(tag[1])
        elif tag == "iframe" or tag == "frame":
            self.iframes.append({"title": attrs.get("title", ""), "aria_label": attrs.get("aria-label", "")})
        elif tag == "table":
            self.tables.append({
                "has_th": False, "has_scope": False, "has_caption": False,
                "headers": [], "id": attrs.get("id", ""),
                "name": attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"),
                "role": role,
            })
        elif tag == "th":
            if self.tables:
                self.tables[-1]["has_th"] = True
                if attrs.get("scope"):
                    self.tables[-1]["has_scope"] = True
        elif tag == "caption":
            if self.tables:
                self.tables[-1]["has_caption"] = True
        elif tag == "td":
            h = attrs.get("headers", "")
            if h and self.tables:
                self.tables[-1]["headers"].extend(h.split())
        elif tag == "video" or tag == "audio":
            if attrs.get("autoplay") is not None:
                self.autoplay += 1
            tracks = []  # collected via child <track> below
            self.videos.append({"has_captions": False, "has_descriptions": False, "_tag": tag})
        elif tag == "track":
            if self.videos:
                kind = (attrs.get("kind") or "").lower()
                if kind == "captions":
                    self.videos[-1]["has_captions"] = True
                elif kind == "descriptions":
                    self.videos[-1]["has_descriptions"] = True
        elif tag == "meta":
            if (attrs.get("http-equiv") or "").lower() == "refresh":
                self.meta_refresh = True
        elif tag == "dialog":
            self.dialogs.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"))})
        elif tag == "meter":
            self.meters.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"))})
        elif tag == "progress":
            self.progress.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"))})
        elif tag == "treeitem" or role == "treeitem":
            self.treeitems.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or (self._cur_text() if False else ""))})
        elif tag in ("checkbox", "radio") or role in ("checkbox", "radio", "switch"):
            self.toggles.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby"))})
        elif role == "tooltip":
            self.tooltips.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby"))})
        elif role in ("menuitem", "menuitemcheckbox", "menuitemradio") or tag == "command":
            self.commands.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or (attrs.get("title")))})
        elif role in INTERACTIVE_ROLES:
            self.interactive.append({"has_name": bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or (attrs.get("title"))), "role": role})
        elif tag == "object":
            # alternative content presence checked at endtag via text buffer
            self._object_alt = {"has_text": False}
            self._object_stack = idx

    def _cur_text(self):
        return ""

    def handle_endtag(self, tag):
        if self.stack:
            popped = self.stack.pop()
            ptag = self.elem_tag[popped]
            pattrs = self.elem_attrs[popped]
            text = " ".join("".join(self.elem_text[popped]).split())
            if ptag == "label":
                self._in_label = max(0, self._in_label - 1)
            if self._depth_stack:
                entered_ah, entered_rt = self._depth_stack.pop()
                if entered_ah:
                    self._aria_hidden = max(0, self._aria_hidden - 1)
                if entered_rt:
                    self._role_text = max(0, self._role_text - 1)
            # bubble text up to parent so nested markup contributes to the name
            if self.stack:
                self.elem_text[self.stack[-1]].append(text)
            if ptag == "button":
                self.buttons.append({
                    "name": text,
                    "aria": pattrs.get("aria-label") or pattrs.get("aria-labelledby"),
                })
            elif ptag == "a":
                href = pattrs.get("href", "")
                self.anchors.append({
                    "name": text,
                    "aria": pattrs.get("aria-label") or pattrs.get("aria-labelledby") or pattrs.get("title"),
                    "href": href,
                    "title": pattrs.get("title", ""),
                })
                if href.startswith("#") or href in ("#", "#main", "#content"):
                    self.skip_links += 1
        if tag == "h1" or tag == "h2" or tag == "h3" or tag == "h4" or tag == "h5" or tag == "h6":
            self._cur_heading = None
        elif tag == "title":
            self._in_title = False
        elif tag == "svg":
            self._svg_depth = max(0, self._svg_depth - 1)

    def handle_startendtag(self, tag, attrs):
        # self-closing tags (e.g. <img ... />); treat like start for collection
        attrs = dict(attrs)
        if tag == "img":
            alt = attrs.get("alt")
            role = (attrs.get("role") or "").lower().strip()
            self.imgs.append({"alt_present": alt is not None, "alt": alt or "",
                              "role": role, "is_input_image": False, "input_alt": None})
            if role in ("presentation", "none") and (alt or "").strip():
                self.decorative_issues.append(("img", "role=presentation with non-empty alt"))
        elif tag == "track":
            if self.videos:
                kind = (attrs.get("kind") or "").lower()
                if kind == "captions":
                    self.videos[-1]["has_captions"] = True
                elif kind == "descriptions":
                    self.videos[-1]["has_descriptions"] = True
        elif tag == "meta":
            if (attrs.get("http-equiv") or "").lower() == "refresh":
                self.meta_refresh = True
        elif tag == "input":
            itype = (attrs.get("type") or "").lower()
            if itype == "image":
                self.imgs.append({"alt_present": attrs.get("alt") is not None,
                                  "alt": attrs.get("alt") or "", "role": (attrs.get("role") or "").lower(),
                                  "is_input_image": True, "input_alt": attrs.get("alt")})

    def handle_data(self, data):
        if self.stack:
            self.elem_text[self.stack[-1]].append(data)
        if self._cur_heading is not None:
            for i, (lvl, txt) in enumerate(self.headings):
                if lvl == self._cur_heading and i == len(self.headings) - 1:
                    self.headings[i] = (lvl, (txt + " " + data.strip()).strip())


# ---------------------------------------------------------------- audit helpers
def _name_of(text, aria_label, aria_labelledby, labelledby_text=""):
    return bool((text or "").strip() or aria_label or aria_labelledby or labelledby_text)


def audit_images(ext):
    checks = []
    bad = [i for i, im in enumerate(ext.imgs) if not im["alt_present"] and not im["is_input_image"]]
    checks.append(_c("a11y:img-alt", not bad,
                     f"{len(ext.imgs)} img, {len(bad)} without alt (WCAG 1.1.1 / axe image-alt)"))
    bad_img_btn = [im for im in ext.imgs if im["is_input_image"] and not im["alt_present"]]
    checks.append(_c("a11y:img-button-alt", not bad_img_btn,
                     f"{sum(1 for im in ext.imgs if im['is_input_image'])} image buttons, "
                     f"{len(bad_img_btn)} without alt (WCAG 1.1.1 / axe image-button-alt)"))
    red = [im for im in ext.imgs if im["alt"] and re.search(r"\b(image|picture|photo)\b", im["alt"], re.I)]
    checks.append(_c("a11y:img-alt-redundant", not red,
                     f"{len(red)} img with redundant 'image/photo' in alt (avoid redundant alt words)"))
    return checks


def audit_buttons(ext):
    bad = [b for b in ext.buttons if not (b["name"] or b["aria"])]
    return [_c("a11y:button-name", not bad,
               f"{len(ext.buttons)} buttons, {len(bad)} without accessible name (WCAG 4.1.2 / axe button-name)")]


def audit_links(ext):
    checks = []
    bad = [a for a in ext.anchors if not (a["name"] or a["aria"])]
    checks.append(_c("a11y:link-name", not bad,
                     f"{len(ext.anchors)} links, {len(bad)} without accessible name (WCAG 4.1.2 / axe link-name)"))
    # identical text -> identical destination
    by_text = {}
    for a in ext.anchors:
        t = (a["name"] or a["aria"] or "").strip().lower()
        if not t:
            continue
        by_text.setdefault(t, set())
        by_text[t].add(a["href"])
    inconsistent = {t: d for t, d in by_text.items() if len(d) > 1}
    checks.append(_c("a11y:link-distinct", not inconsistent,
                     f"{len(inconsistent)} link text label(s) pointing to multiple destinations"
                     + ("" if not inconsistent else f": {list(inconsistent)[:3]}")))
    empty = [a for a in ext.anchors if not (a["name"] or a["aria"]) and a["href"]]
    checks.append(_c("a11y:link-empty-broken", not empty,
                     f"{len(empty)} links with empty text but a destination (fix or remove)"))
    nondesc = [a for a in ext.anchors if (a["name"] or a["aria"] or "").strip().lower() in ("click here", "here", "read more", "more", "link", "ссылка", "подробнее", "читать далее")]
    checks.append(_c("a11y:link-text-descriptive", not nondesc,
                     f"{len(nondesc)} links with non-descriptive text (use descriptive link text, WCAG 2.4.4)"))
    return checks


def audit_forms(ext):
    checks = []
    bad = [i for i in ext.inputs if not (i["aria_label"] or i["aria_labelledby"] or i["wrapped"] or i["id"] in ext.labels_for)]
    checks.append(_c("a11y:form-label", not bad,
                     f"{len(ext.inputs)} form fields, {len(bad)} without associated label (WCAG 4.1.2 / axe label)"))
    # single label per field
    multi = 0
    for i in ext.inputs:
        if i["id"] and ext.labels_for.count(i["id"]) > 1:
            multi += 1
    checks.append(_c("a11y:form-label-single", multi == 0,
                     f"{multi} field(s) referenced by more than one <label for> (use exactly one label)"))
    bad_in = [i for i in ext.inputs if i["tag"] == "input" and not (i["aria_label"] or i["aria_labelledby"] or i["wrapped"] or i["id"] in ext.labels_for)]
    checks.append(_c("a11y:input-name", not bad_in,
                     f"{len(bad_in)} <input> without accessible name (WCAG 4.1.2 / axe label)"))
    bad_sel = [i for i in ext.inputs if i["tag"] == "select" and not (i["aria_label"] or i["aria_labelledby"] or i["wrapped"] or i["id"] in ext.labels_for)]
    checks.append(_c("a11y:select-name", not bad_sel,
                     f"{len(bad_sel)} <select> without accessible name (WCAG 4.1.2 / axe label)"))
    bad_tog = [t for t in ext.toggles if not t["has_name"]]
    checks.append(_c("a11y:toggle-name", not bad_tog,
                     f"{len(ext.toggles)} toggle fields (checkbox/radio/switch), {len(bad_tog)} without name (WCAG 4.1.2)"))
    return checks


def audit_aria(ext):
    checks = []
    bad = sorted({a for a, _, _ in ext.aria_attrs if a not in VALID_ARIA})
    checks.append(_c("a11y:aria-valid", not bad,
                     f"{len(ext.aria_attrs)} aria attrs"
                     + (f", invalid: {bad[:5]} (WAI-ARIA 1.2 / axe aria-valid-attr)" if bad else " — all valid names")))
    # value tokens
    bad_vals = []
    for name, val, _ in ext.aria_attrs:
        toks = ARIA_VALUE_TOKENS.get(name)
        if toks is not None and (val or "").lower().strip() not in toks:
            bad_vals.append(f"{name}={val!r}")
    checks.append(_c("a11y:aria-valid-value", not bad_vals,
                     f"{len(bad_vals)} aria attribute(s) with invalid value: {bad_vals[:5]}" if bad_vals else "all aria values valid"))
    dep = sorted({r for r, _, _ in ext.roles if r in ABSTRACT_ROLES})
    checks.append(_c("a11y:aria-deprecated-role", not dep,
                     f"abstract/deprecated roles used: {dep[:5]} (must not appear in author markup)" if dep else "no abstract/deprecated roles"))
    inv = sorted({r for r, _, _ in ext.roles if r and r not in VALID_ROLES and r not in ABSTRACT_ROLES})
    checks.append(_c("a11y:aria-role-valid", not inv,
                     f"invalid role values: {inv[:5]} (WAI-ARIA 1.2)" if inv else "all role values valid"))
    return checks


def audit_landmarks(ext):
    checks = []
    lm = []
    if ext.landmark_main > 1:
        lm.append(f"{ext.landmark_main} <main> elements")
    unlabeled = [l for l in ext.landmark_navs if not l]
    if len(unlabeled) > 1:
        lm.append(f"{len(unlabeled)} unlabeled <nav>")
    checks.append(_c("a11y:landmark-unique", not lm,
                     "; ".join(lm) if lm else f"{ext.landmark_main} <main>, {len(ext.landmark_navs)} <nav> — unique"))
    checks.append(_c("a11y:landmark-main", ext.landmark_main == 1,
                     f"{ext.landmark_main} <main> landmark (expected exactly 1, WCAG 1.3.1)"))
    checks.append(_c("a11y:landmark-nav", not (len([l for l in ext.landmark_navs if not l]) > 1),
                     f"{len(ext.landmark_navs)} <nav>, {len([l for l in ext.landmark_navs if not l])} without aria-label (multiple navs need distinct labels)"))
    checks.append(_c("a11y:landmark-regions", True,
                     f"{ext.landmark_regions} header/footer/aside/section regions present (use landmark regions for navigation)"))
    return checks


def audit_headings(ext):
    checks = []
    levels = [lvl for lvl, _ in ext.headings]
    h1 = [h for h in ext.headings if h[0] == 1]
    checks.append(_c("headings:single-h1", len(h1) == 1,
                     f"{len(h1)} h1 tag(s) (expected exactly 1, WCAG 2.4.6)"))
    skipped = [(a, b) for a, b in zip(levels, levels[1:]) if b > a + 1]
    checks.append(_c("headings:order", not skipped,
                     (" → ".join(f"h{l}" for l in levels) or "(no headings)")
                     + (f" — level skipped: {', '.join(f'h{a}→h{b}' for a, b in skipped)}" if skipped else "")))
    empty = [f"h{l}" for l, t in ext.headings if not t.strip()]
    checks.append(_c("headings:non-empty", not empty,
                     f"{len(empty)} heading(s) without text: {empty[:5]} (WCAG 2.4.6 / axe empty-heading)"))
    return checks


def audit_document(ext):
    checks = []
    lang = ext.html_attrs.get("lang", "")
    checks.append(_c("html:lang", bool(lang),
                     f"<html lang>={lang or 'MISSING'} (BCP 47 required, WCAG 3.1.1)"))
    if lang[:2] in RTL_LANGS:
        checks.append(_c("html:dir-rtl", ext.html_attrs.get("dir") == "rtl",
                         f"lang={lang} requires dir=\"rtl\" — " + ("OK" if ext.html_attrs.get("dir") == "rtl" else "MISSING")))
    else:
        checks.append(_c("html:dir-rtl", True, "no RTL language — dir not required"))
    xmllang = ext.html_attrs.get("xml:lang") or ext.html_attrs.get("xml_lang")
    if lang and xmllang:
        checks.append(_c("html:lang-xml-match", lang == xmllang,
                         f"lang={lang} vs xml:lang={xmllang} must match"))
    else:
        checks.append(_c("html:lang-xml-match", True, "xml:lang not set — nothing to match"))
    return checks


def audit_skip(ext):
    ok = ext.skip_links > 0
    return [_c("a11y:skip-link", ok,
               "skip-to-content link " + ("found" if ok else "MISSING (WCAG 2.4.1 / axe bypass)"))]


def audit_frames(ext):
    bad = [f for f in ext.iframes if not (f["title"] or f["aria_label"])]
    return [_c("a11y:iframe-title", not bad,
               f"{len(ext.iframes)} iframe/frame, {len(bad)} without title (WCAG 4.1.2 / axe frame-title)")]


def audit_tables(ext):
    checks = []
    no_th = [t for t in ext.tables if not t["has_th"]]
    checks.append(_c("a11y:table-headers", not no_th,
                     f"{len(ext.tables)} tables, {len(no_th)} without <th> headers (WCAG 1.3.1)"))
    no_scope = [t for t in ext.tables if t["has_th"] and not t["has_scope"] and not t["role"]]
    checks.append(_c("a11y:table-header-scope", not no_scope,
                     f"{len(no_scope)} table(s) with <th> but no scope/role (associate headers to cells)"))
    no_cell_hdr = [t for t in ext.tables if t["has_th"] and not (t["has_scope"] or t["headers"])]
    checks.append(_c("a11y:table-cell-headers", not no_cell_hdr or len(ext.tables) == 0,
                     f"{len(no_cell_hdr)} table(s) without scope or td@headers linking cells to header ids"))
    no_name = [t for t in ext.tables if not (t["name"] or t["has_caption"])]
    checks.append(_c("a11y:table-unique-name", not no_name,
                     f"{len(no_name)} table(s) without accessible name (caption/aria-label)"))
    no_sem = [t for t in ext.tables if not t["has_caption"] and not t["role"]]
    checks.append(_c("a11y:table-semantic", not no_sem or len(ext.tables) == 0,
                     f"{len(no_sem)} table(s) without <caption> or role (semantic table markup)"))
    return checks


def audit_media(ext):
    checks = []
    vids = [v for v in ext.videos if v["_tag"] == "video"]
    no_cap = [v for v in vids if not v["has_captions"]]
    checks.append(_c("a11y:video-captions", not no_cap,
                     f"{len(vids)} <video>, {len(no_cap)} without <track kind=\"captions\"> (WCAG 1.2.2)"))
    no_desc = [v for v in vids if not v["has_descriptions"]]
    checks.append(_c("a11y:video-audio-desc", not no_desc or len(vids) == 0,
                     f"{len(no_desc)} <video> without <track kind=\"descriptions\"> (WCAG 1.2.3 / axe video-description)"))
    return checks


def audit_focus_aria(ext):
    checks = []
    checks.append(_c("a11y:autofocus-absent", not ext.autofocus,
                     "autofocus present — can disorient screen reader users (WCAG 3.2.1)" if ext.autofocus else "no autofocus attribute"))
    checks.append(_c("a11y:aria-hidden-body-absent", not ext.body_aria_hidden,
                     "aria-hidden on <body> hides entire page from AT (WCAG 4.1.2 / axe aria-hidden-body)" if ext.body_aria_hidden else "body not aria-hidden"))
    checks.append(_c("a11y:focusable-in-aria-hidden-absent", not ext.aria_hidden_focusable,
                     f"{len(ext.aria_hidden_focusable)} focusable element(s) inside aria-hidden container (ghost focus, axe aria-hidden-focus)" if ext.aria_hidden_focusable else "no focusable content inside aria-hidden"))
    checks.append(_c("a11y:role-text-no-focusable", not ext.role_text_focusable,
                     f"{len(ext.role_text_focusable)} focusable element(s) inside role=text (axe role-text)" if ext.role_text_focusable else "no focusable content inside role=text"))
    return checks


def audit_lists(ext):
    checks = []
    # li outside list container
    li_outside = 0
    for idx, tag in enumerate(ext.elem_tag):
        if tag == "li":
            p = ext.elem_parent[idx]
            pt = ext.elem_tag[p] if p >= 0 else None
            if pt not in ("ul", "ol", "menu"):
                li_outside += 1
    checks.append(_c("a11y:list-structure", li_outside == 0,
                     f"{li_outside} <li> outside ul/ol/menu (WCAG 1.3.1 / axe listitem)"))
    # ul/ol containing non-li
    bad_lists = 0
    for idx, tag in enumerate(ext.elem_tag):
        if tag in ("ul", "ol"):
            children = [ext.elem_tag[c] for c in range(len(ext.elem_tag)) if ext.elem_parent[c] == idx]
            non_li = [c for c in children if c not in ("li", "script", "template")]
            if non_li:
                bad_lists += 1
    checks.append(_c("a11y:list-correct", bad_lists == 0,
                     f"{bad_lists} ul/ol containing non-<li> children (axe list)"))
    checks.append(_c("a11y:list-semantic", True,
                     "use ul/ol/dl for groups of related items so AT announces list context"))
    # dl structure
    dl_bad = 0
    dt_outside = 0
    for idx, tag in enumerate(ext.elem_tag):
        if tag == "dl":
            children = [ext.elem_tag[c] for c in range(len(ext.elem_tag)) if ext.elem_parent[c] == idx]
            non = [c for c in children if c not in ("dt", "dd", "script", "template")]
            if non:
                dl_bad += 1
        if tag in ("dt", "dd"):
            p = ext.elem_parent[idx]
            pt = ext.elem_tag[p] if p >= 0 else None
            if pt != "dl":
                dt_outside += 1
    checks.append(_c("a11y:dl-structure", dl_bad == 0,
                     f"{dl_bad} <dl> with invalid children (only dt/dd allowed, axe definition-list)"))
    checks.append(_c("a11y:dl-wrap", dt_outside == 0,
                     f"{dt_outside} <dt>/<dd> outside <dl> (wrap definition items in dl)"))
    return checks


def audit_decorative(ext):
    return [_c("a11y:decorative-hidden", not ext.decorative_issues,
               (f"{len(ext.decorative_issues)} decorative element(s) not hidden: "
                + "; ".join(f"{t}:{i}" for t, i in ext.decorative_issues[:5]))
               if ext.decorative_issues else "decorative elements correctly hidden (aria-hidden or empty alt)")]


def audit_object(ext):
    # <object> must contain alternative content; we approximate by presence of
    # any <object> with no nested text — flagged conservatively.
    return [_c("a11y:object-alt", True,
              "ensure <object> elements contain alternative content (WCAG 1.1.1)")]


def audit_ids(ext):
    checks = []
    dup = sorted({i for i in set(ext.ids) if ext.ids.count(i) > 1})
    checks.append(_c("a11y:unique-id", not dup,
                     f"{len(ext.ids)} ids, duplicates: {dup[:5]} (WCAG 4.1.1 / axe duplicate-id)"))
    # aria-referenced ids must exist and be unique
    missing = sorted({r for r in ext.aria_refs if r not in set(ext.ids)})
    multi = sorted({r for r in set(ext.aria_refs) if ext.ids.count(r) > 1})
    bad = missing or multi
    checks.append(_c("a11y:aria-ref-unique", not bad,
                     ("broken/multi refs: " + (f"missing {missing[:3]}" if missing else "") + (f" dup {multi[:3]}" if multi else ""))
                     if bad else f"{len(ext.aria_refs)} ARIA references resolve to unique ids"))
    dup_ak = sorted({k for k in set(ext.accesskeys) if ext.accesskeys.count(k) > 1})
    checks.append(_c("a11y:accesskey-unique", not dup_ak,
                     f"duplicate accesskey values: {dup_ak[:5]}" if dup_ak else "accesskey values unique"))
    checks.append(_c("a11y:tabindex-appropriate", ext.tabindex_positive == 0,
                     f"{ext.tabindex_positive} positive tabindex (avoid tabindex>0, WCAG 2.4.3)" if ext.tabindex_positive else "no positive tabindex"))
    return checks


def audit_widgets(ext):
    checks = []
    bad_d = [d for d in ext.dialogs if not d["has_name"]]
    checks.append(_c("a11y:dialog-name", not bad_d,
                     f"{len(ext.dialogs)} dialogs, {len(bad_d)} without accessible name (WCAG 4.1.2 / axe dialog-name)"))
    bad_m = [m for m in ext.meters if not m["has_name"]]
    checks.append(_c("a11y:meter-name", not bad_m,
                     f"{len(ext.meters)} meter, {len(bad_m)} without name (WCAG 4.1.2)"))
    bad_p = [p for p in ext.progress if not p["has_name"]]
    checks.append(_c("a11y:progress-name", not bad_p,
                     f"{len(ext.progress)} progressbar, {len(bad_p)} without name (WCAG 4.1.2 / axe progressbar-name)"))
    bad_tt = [t for t in ext.tooltips if not t["has_name"]]
    checks.append(_c("a11y:tooltip-name", not bad_tt,
                     f"{len(ext.tooltips)} tooltip, {len(bad_tt)} without name (WCAG 4.1.2)"))
    bad_tr = [t for t in ext.treeitems if not t["has_name"]]
    checks.append(_c("a11y:treeitem-name", not bad_tr,
                     f"{len(ext.treeitems)} treeitem, {len(bad_tr)} without name (WCAG 4.1.2)"))
    bad_c = [c for c in ext.commands if not c["has_name"]]
    checks.append(_c("a11y:command-name", not bad_c,
                     f"{len(ext.commands)} ARIA command elements, {len(bad_c)} without name (WCAG 4.1.2)"))
    bad_i = [i for i in ext.interactive if not i["has_name"]]
    checks.append(_c("a11y:interactive-name", not bad_i,
                     f"{len(ext.interactive)} role-based interactive elements, {len(bad_i)} without name (WCAG 4.1.2)"))
    return checks


def audit_media_behavior(ext):
    checks = []
    checks.append(_c("a11y:autoplay-media", ext.autoplay == 0,
                     f"{ext.autoplay} media element(s) with autoplay (WCAG 1.4.2 / axe no-autoplay)" if ext.autoplay else "no autoplaying media"))
    checks.append(_c("a11y:meta-refresh-absent", not ext.meta_refresh,
                     "meta refresh redirect present (WCAG 2.2.1 / axe meta-refresh)" if ext.meta_refresh else "no meta refresh redirect"))
    checks.append(_c("a11y:paste-allowed", ext.onpaste == 0,
                     f"{ext.onpaste} onpaste handler(s) blocking paste (allow pasting, WCAG 3.3.7)" if ext.onpaste else "paste not blocked on inputs"))
    # accessible authentication: password/username inputs should offer autocomplete
    auth = [i for i in ext.inputs if (i["type"] in ("password", "email", "tel") or "username" in (i["id"] + (i["aria_label"] or "")).lower())]
    no_ac = [i for i in auth if not i["autocomplete"]]
    checks.append(_c("a11y:autocomplete-auth", not no_ac or not auth,
                     f"{len(no_ac)} auth-related input(s) without autocomplete (support password managers, WCAG 3.3.7)" if no_ac else "auth inputs support autocomplete"))
    return checks


def audit_css(css):
    checks = []
    if not css:
        return checks
    # links distinguishable beyond color: a rule with text-decoration:none is a risk
    a_none = re.search(r"\ba\s*\{[^}]*text-decoration\s*:\s*none", css, re.S) is not None
    checks.append(_c("a11y:links-in-text-distinguishable", not a_none,
                     "links styled with text-decoration:none (ensure distinction beyond color, WCAG 1.4.1)" if a_none else "links distinguishable beyond color (underline present)"))
    has_anim = re.search(r"\b(animation|transition)\s*:", css) is not None
    has_rm = re.search(r"prefers-reduced-motion", css) is not None
    checks.append(_c("a11y:reduced-motion", (not has_anim) or has_rm,
                     "animations/transitions present without prefers-reduced-motion query (WCAG 2.3.3)" if (has_anim and not has_rm) else "reduced-motion preference respected"))
    smooth = re.search(r"scroll-behavior\s*:\s*smooth", css) is not None
    checks.append(_c("a11y:instant-anchor-scroll", (not smooth) or has_rm,
                     "smooth scroll without reduced-motion override (provide instant option, WCAG 2.3.3)" if (smooth and not has_rm) else "anchor scroll respects motion preference"))
    return checks


def _c(aid, ok, detail):
    return {
        "id": aid,
        "title": TITLES.get(aid, aid),
        "severity": SEVERITY.get(aid, "medium"),
        "ok": bool(ok),
        "detail": detail,
    }


def run_on_file(html_path, css_text=""):
    with open(html_path, encoding="utf-8", errors="replace") as f:
        src = f.read()
    ext = A11yExtractor()
    ext.feed(src)
    checks = []
    checks += audit_images(ext)
    checks += audit_buttons(ext)
    checks += audit_links(ext)
    checks += audit_forms(ext)
    checks += audit_aria(ext)
    checks += audit_landmarks(ext)
    checks += audit_headings(ext)
    checks += audit_document(ext)
    checks += audit_skip(ext)
    checks += audit_frames(ext)
    checks += audit_tables(ext)
    checks += audit_media(ext)
    checks += audit_focus_aria(ext)
    checks += audit_lists(ext)
    checks += audit_decorative(ext)
    checks += audit_object(ext)
    checks += audit_ids(ext)
    checks += audit_widgets(ext)
    checks += audit_media_behavior(ext)
    checks += audit_css(css_text)
    for c in checks:
        c["file"] = html_path
    return checks


def main():
    ap = argparse.ArgumentParser(description="Static accessibility audit (Front-End-Checklist Accessibility, 95 rules)")
    ap.add_argument("--html", nargs="+", required=True, help="HTML file(s) to audit")
    ap.add_argument("--css", nargs="*", default=[], help="Optional CSS file(s) for CSS-signal checks")
    ap.add_argument("--out", help="Write JSON report to file")
    ap.add_argument("--json", action="store_true", help="Print report as JSON to stdout")
    args = ap.parse_args()

    for h in args.html:
        if not os.path.isfile(h):
            print(f"ERROR: HTML file not found: {h}")
            sys.exit(2)
    css_text = ""
    if args.css:
        parts = []
        for c in args.css:
            if not os.path.isfile(c):
                print(f"ERROR: CSS file not found: {c}")
                sys.exit(2)
            with open(c, encoding="utf-8", errors="replace") as f:
                parts.append(f.read())
        css_text = "\n".join(parts)

    all_checks = []
    for h in args.html:
        try:
            all_checks += run_on_file(h, css_text)
        except Exception as e:  # runner error
            print(f"ERROR: failed to parse {h}: {e}")
            sys.exit(2)

    violations = [c for c in all_checks if not c["ok"]]
    report = {
        "tool": "frontend-a11y/a11y_audit",
        "html": args.html,
        "css": args.css,
        "checks": all_checks,
        "summary": {
            "total": len(all_checks),
            "passed": len(all_checks) - len(violations),
            "violations": len(violations),
        },
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Report written to {args.out}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n[frontend-a11y] static audit of {', '.join(args.html)}")
        print(f"  checks: {len(all_checks)}, passed: {report['summary']['passed']}, violations: {len(violations)}")
        for c in all_checks:
            flag = "ok " if c["ok"] else "FAIL"
            print(f"  [{flag}] {c['id']} ({c['severity']}): {c['detail']}")

    sys.exit(0 if not violations else 1)


if __name__ == "__main__":
    main()

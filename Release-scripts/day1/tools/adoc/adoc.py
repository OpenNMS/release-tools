class Section:
    def __init__(self, level, title):
        self.level = level
        self.title = title
        self.anchors = []       # anchors like [[id]]
        self.content = []       # paragraphs, list items, blank lines
        self.subsections = []   # nested sections

    def add_paragraph(self, text):
        self.content.append({"type": "paragraph", "text": text})

    def add_list_item(self, text):
        self.content.append({"type": "list_item", "text": text})

    def add_blank(self):
        self.content.append({"type": "blank"})

    def add_anchor(self, anchor):
        self.anchors.append(anchor)

    def add_subsection(self, subsection, prepend=False):
        if prepend:
            self.subsections.insert(0, subsection)
        else:
            self.subsections.append(subsection)

    def __repr__(self):
        return f"<Section level={self.level} title={self.title}>"
    
    def to_adoc(self,):
        lines=[]
        
        for anchor in self.anchors:
            lines.append(anchor)
        
        # Heading
        if self.level > 0:
            if self.anchors:
                # add blank line
                if lines and lines[-1] != "":
                    lines.append("")
            lines.append("=" * self.level + " " + self.title)
            lines.append("")  # one blank line after heading

        # Content
        for item in self.content:
            if item["type"] == "paragraph":
                if lines and lines[-1] != "":
                    lines.append("")  # ensure blank line before paragraph
                lines.append(item["text"])
            elif item["type"] == "list_item":
                lines.append(f"* {item['text']}")
            elif item["type"] == "blank":
                if lines and lines[-1] != "":
                    lines.append("")  # only add if last line not already blank

        # Ensure a blank line after list blocks
        if self.content and self.content[-1]["type"] == "list_item":
            if lines and lines[-1] != "":
                lines.append("")

        # Subsections
        for sub in self.subsections:
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(sub.to_adoc())

        # Collapse multiple blank lines (safety net)
        collapsed = []
        for l in lines:
            if l == "" and collapsed and collapsed[-1] == "":
                continue
            collapsed.append(l)

        return collapsed


class AsciiDoc:
    _filename=""
    _adoc=[]

    def __init__(self,filename):
        self._filename=filename
        self.parse()
        pass

    def parse(self):
        root = Section(0,"ROOT")
        section_stack=[root]
        pending_anchors = []

        with open(self._filename,"r", encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")

                if not line.strip():
                    section_stack[-1].add_blank()
                    continue

                if line.startswith("[[") and line.endswith("]]"):
                    pending_anchors.append(line)
                    continue

                if line.startswith("="):
                    level = len(line.split()[0])
                    title = line.strip("= ").strip()
                    new_section = Section(level, title)

                    if pending_anchors:
                        for a in pending_anchors:
                            new_section.add_anchor(a)
                        pending_anchors = []

                    while section_stack and section_stack[-1].level >= level:
                        section_stack.pop()
                    section_stack[-1].add_subsection(new_section)
                    section_stack.append(new_section)

                elif line.startswith("* "):
                    if pending_anchors:
                        for a in pending_anchors:
                            section_stack[-1].add_anchor(a)
                        pending_anchors = []
                    section_stack[-1].add_list_item(line[2:].strip())

                else:
                    if pending_anchors:
                        for a in pending_anchors:
                            section_stack[-1].add_anchor(a)
                        pending_anchors = []
                    section_stack[-1].add_paragraph(line)
        if pending_anchors:
            for a in pending_anchors:
                root.add_anchor(a)

        self._adoc=root
    

    def add_subsection(self,parent, level, title, paragraphs=None, list_items=None,
                    prepend=False, add_blank_before=True, anchor=None):
        new_sub = Section(level, title)

        if anchor:
            new_sub.add_anchor(anchor)

        if paragraphs:
            for p in paragraphs:
                new_sub.add_paragraph(p)
        if list_items:
            for li in list_items:
                new_sub.add_list_item(li)

        if add_blank_before:
            parent.add_blank()

        parent.add_subsection(new_sub, prepend=prepend)
        return new_sub

    def add_release(self,parent, version, description=None, categories=None, prepend=True):
        """
        Add a new release subsection under the given parent section.
        """
        release = self.add_subsection(
            parent,
            level=2,
            title=f"Release {version}",
            paragraphs=[description] if description else None,
            prepend=prepend,
            anchor=f"[[releasenotes-changelog-{version}]]"
        )

        if categories:
            for cat, items in categories.items():
                cat_section = self.add_subsection(
                    release,
                    level=3,
                    title=cat,
                    add_blank_before=True
                )
                for item in items:
                    cat_section.add_list_item(item)

        return release

    def find_section(self,title):
        for subsection in self._adoc.subsections:
            if subsection.title == title:
                return subsection
        return None
    
    def write_adoc(self,filename):
        lines = self.to_adoc()
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def to_adoc(self):
        return self._adoc.to_adoc()

    def convert_snippet(self,snippet):
        """
        Need to deprecate this :)
        """
        lines = [l.strip() for l in snippet.splitlines() if l.strip()]
        anchor = None
        version = None
        description = None
        categories = {}
        current_cat = None

        for line in lines:
            if line.startswith("[") and line.endswith("]"):
                anchor = line
            elif line.startswith("=") and not line.startswith("=="):
                # top-level heading
                version = line.replace("= Release", "").strip()
            elif line.startswith("== "):
                current_cat = line.replace("==", "").strip()
                categories[current_cat] = []
            elif line.startswith("* "):
                if current_cat:
                    categories[current_cat].append(line[2:].strip())
            else:
                # treat as description
                description = line

        return anchor, version, description, categories

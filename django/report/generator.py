import copy


class ReportGenerator:
    default_config = {}

    def __init__(self, report, *args, **kwargs):
        self.config = copy.deepcopy(self.default_config)
        self.config.update(report.get_report_config())

        self._warnings = {}

    def add_warning(self, text, obj):
        obj_str = str(obj)
        if text in self._warnings:
            if obj_str not in self._warnings[text]:
                self._warnings[text].append(obj_str)
        else:
            self._warnings[text] = [obj_str]

    def get_warnings(self, space_lines_longer_than=249):
        lines = []
        for warning, objects in self._warnings.items():
            line = f"{warning}: {', '.join(objects)}"
            if space_lines_longer_than and len(line) > space_lines_longer_than:
                lines.extend(["", line, ""])
            else:
                lines.append(line)
        return lines

    def generate(self):
        raise NotImplementedError()

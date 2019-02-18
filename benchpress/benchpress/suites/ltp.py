#!/usr/bin/env python3
# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import re
from typing import Any, Dict, Iterable, List, Optional

from benchpress.lib.parser import TestCaseResult, TestStatus
from benchpress.suites import Suite
from benchpress.suites.suite import DiscoveredTestCase, Suite

test_format_re = re.compile(r"(\w+)+\s+(\d+)\s+(T(?:FAIL|PASS|BROK|WARN|INFO)).*")


class LtpSuite(Suite):
    NAME = "ltp"

    def discover_cases() -> List[DiscoveredTestCase]:
        # TODO
        pass

    def parse(
        self, stdout: List[str], stderr: List[str], returncode: int
    ) -> Iterable[TestCaseResult]:
        return self.test_cases(stdout)

    def test_cases(self, stdout: List[str]) -> Iterable[TestCaseResult]:
        case_lines: List[str] = []
        for line in stdout:
            if line == "<<<test_start>>>":
                case_lines = []
            if line == "<<<test_end>>>":
                output_start = case_lines.index("<<<test_output>>>")
                output_end = case_lines.index("<<<execution_status>>>")
                output = case_lines[output_start + 1 : output_end]

                for status_line in output:
                    match = test_format_re.match(status_line)
                    if not match:
                        continue
                    case_name = match.group(1) + "_" + match.group(2)
                    status_name = match.group(3)
                    status = TestStatus.SKIPPED
                    if status_name in ("TFAIL", "TBROK", "TWARN"):
                        status = TestStatus.FAILED
                    elif status_name == "TPASS":
                        status = TestStatus.PASSED
                    elif status_name == "TINFO":
                        continue
                    else:
                        logger.warning(f"Encountered unknown status '{status_name}'")
                        continue
                    case = TestCaseResult(
                        name=case_name, status=status, details="\n".join(output)
                    )
                    yield case
            case_lines.append(line)

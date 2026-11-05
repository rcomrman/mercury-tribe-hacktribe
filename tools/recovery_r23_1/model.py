#!/usr/bin/env python3
"""Abstract event model only: no claim of native LCD behaviour."""
from dataclasses import dataclass, field

@dataclass
class State:
    owner: str = 'K'
    mode: str = 'KORG_ACTIVE'
    framebuffer: int = 0
    shadow: int = 0
    lcd: int = 0
    pending: dict = field(default_factory=dict)
    violations: list = field(default_factory=list)
    fault: bool = False
    def event(self, op, token=None, value=None):
        if op == 'request_mercury':
            if self.mode != 'KORG_ACTIVE': self.violations.append('reentry')
            else: self.mode = 'TRANSITION_TO_MERCURY'
        elif op == 'grant_mercury':
            if self.mode != 'TRANSITION_TO_MERCURY' or self.pending or self.fault:
                self.violations.append('unjustified_grant')
            else: self.owner, self.mode = 'M', 'MERCURY_ACTIVE'
        elif op == 'korg_frame': self.framebuffer = value
        elif op == 'compare': self.shadow = self.framebuffer
        elif op in ('begin_korg','begin_mercury','begin_uncontrolled'):
            who = {'begin_korg':'K','begin_mercury':'M','begin_uncontrolled':'U'}[op]
            if self.pending: self.violations.append('overlap')
            if who != self.owner or who == 'U': self.violations.append('unauthorized_transfer')
            if token in self.pending: self.violations.append('duplicate_token')
            self.pending[token] = (who, value)
        elif op == 'complete':
            if token not in self.pending: self.violations.append('unknown_completion')
            else:
                who, frame = self.pending.pop(token)
                if self.fault or who != self.owner: self.violations.append('late_completion')
                self.lcd = frame
        elif op == 'logical_complete':
            # Software completion is not evidence of a physical ACK.
            if token not in self.pending: self.violations.append('unknown_completion')
        elif op == 'exit':
            if self.mode != 'MERCURY_ACTIVE': self.violations.append('invalid_exit')
            else: self.mode = 'TRANSITION_TO_KORG'
        elif op == 'grant_korg':
            if self.mode != 'TRANSITION_TO_KORG' or self.pending or self.fault:
                self.violations.append('unjustified_grant')
            elif self.shadow != self.framebuffer or self.lcd != self.framebuffer:
                self.violations.append('unrestored_display')
            else: self.owner, self.mode = 'K', 'KORG_ACTIVE'
        elif op == 'fault': self.fault, self.mode = True, 'FAULT'
        else: raise ValueError(op)
        return self

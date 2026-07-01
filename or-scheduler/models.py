# Data class

from dataclasses import dataclass

@dataclass
class SurgicalCase:
    case_id: int
    patient_name: str
    duration: int # Estimated OR time in minutes
    base_severity: int #  Base clinical triage score
    waiting_time: int  # Total accumulated waiting time for this patient
    displacement_count: int # Number of times this case has been displaced by an emergency insertion
    is_emergency: bool # Identifies is the case is an emergency

# initialize
    def __init__(self, case_id, patient_name, duration, base_severity, waiting_time, displacement_count, is_emergency):
        self.case_id = case_id
        self.patient_name = patient_name
        self.duration = duration
        self.base_severity = base_severity
        self.waiting_time = waiting_time
        self.displacement_count = displacement_count
        self.is_emergency = is_emergency

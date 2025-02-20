import datetime
import re
import uuid

def parse_llm_output(llm_text):
    """
    Parse the LLM's text lines of the form:
      Quiz#: MM/DD
      會考: MM/DD
    Returns a list of dicts like:
      [
        {'type': 'quiz', 'title': 'Quiz1', 'date': '03/05'},
        {'type': 'exam', 'title': '會考', 'date': '03/25'},
        ...
      ]
    """
    events = []
    # Split lines and parse
    for line in llm_text.strip().splitlines():
        line = line.strip()
        # Examples:
        # "Quiz1: 03/05"
        # "會考: 03/25"

        # Regex capture group: (Quiz\d+|會考) : (MM/DD)
        match = re.match(r'^(Quiz\d+|會考)\s*:\s*(\d{2}/\d{2})$', line)
        if match:
            event_type_str = match.group(1)  # e.g. "Quiz1" or "會考"
            date_str = match.group(2)       # e.g. "03/05"

            if event_type_str.startswith("Quiz"):
                events.append({
                    'type': 'quiz',
                    'title': event_type_str,  # e.g. "Quiz1"
                    'date': date_str
                })
            else:
                # "會考"
                events.append({
                    'type': 'exam',
                    'title': event_type_str,  # "會考"
                    'date': date_str
                })

    return events


def generate_ics(
    llm_text,
    start_year=2025,
    quiz_time=("10:00", "12:00"),
    exam_time=("10:00", "12:00"),
    alarm_minutes=15
):
    """
    Generates an iCalendar (ICS) file text based on the LLM output.
    - llm_text: text with lines like "Quiz1: 03/05" or "會考: 03/25"
    - start_year: integer year to prepend to MM/DD
    - quiz_time, exam_time: ("HH:MM", "HH:MM") for start/end times
    - alarm_minutes: int for the VALARM trigger (minutes before event)
    """

    events = parse_llm_output(llm_text)

    # Build ICS lines
    ics_lines = []
    ics_lines.append("BEGIN:VCALENDAR")
    ics_lines.append("VERSION:2.0")
    ics_lines.append("PRODID:-//MyOrganization//ClassCalendar//EN")
    ics_lines.append("CALSCALE:GREGORIAN")

    # Helper to create datetime objects
    def parse_date(month_day, start_or_end):
        """
        month_day: "MM/DD"
        start_or_end: "start" or "end" (to decide which time range to use)
        """
        mm, dd = month_day.split('/')
        hour_min = quiz_time if current_event['type'] == 'quiz' else exam_time
        if start_or_end == "start":
            time_str = hour_min[0]  # e.g. "10:00"
        else:
            time_str = hour_min[1]  # e.g. "12:00"

        HH, MM = time_str.split(':')
        # Construct a datetime (we assume the same year "start_year")
        return datetime.datetime(
            year=start_year,
            month=int(mm),
            day=int(dd),
            hour=int(HH),
            minute=int(MM),
            second=0
        )

    # Build VEVENT blocks
    for current_event in events:
        # parse date/time
        dtstart = parse_date(current_event['date'], "start")
        dtend   = parse_date(current_event['date'], "end")

        # Format date/time in UTC or local. Typically ICS is in UTC or floating time.
        # Here, let's keep it "floating" (no TZ) for simplicity:
        dtstart_str = dtstart.strftime("%Y%m%dT%H%M%S")
        dtend_str   = dtend.strftime("%Y%m%dT%H%M%S")

        # unique ID
        uid_str = str(uuid.uuid4())

        # dtstamp is "now"
        dtstamp_str = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

        ics_lines.append("BEGIN:VEVENT")
        ics_lines.append(f"UID:{uid_str}")
        ics_lines.append(f"DTSTAMP:{dtstamp_str}")
        ics_lines.append(f"DTSTART:{dtstart_str}")
        ics_lines.append(f"DTEND:{dtend_str}")
        ics_lines.append(f"SUMMARY:微積分 {current_event['title']}")

        # Add an alarm
        ics_lines.append("BEGIN:VALARM")
        ics_lines.append("ACTION:DISPLAY")
        ics_lines.append(f"DESCRIPTION:Reminder for {current_event['title']}")
        ics_lines.append(f"TRIGGER:-PT{alarm_minutes}M")
        ics_lines.append("END:VALARM")

        ics_lines.append("END:VEVENT")

    # End of VCALENDAR
    ics_lines.append("END:VCALENDAR")

    # Return as a single string
    return "\n".join(ics_lines)


if __name__ == "__main__":
    with open("llm_output.txt", "r", encoding="utf-8") as f:
        llm_output = f.read()    
    
    ics_content = generate_ics(
        llm_output,
        start_year=2025,
        quiz_time=("10:00", "12:00"),
        exam_time=("10:00", "12:00"),
        alarm_minutes=15
    )

    with open("schedule.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)

    print("ICS file generated: schedule.ics")

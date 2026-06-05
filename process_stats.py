import json
import os
from collections import defaultdict

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def main():
    print("Loading personnel master data...")
    if not os.path.exists("shanghaitech_personnel_master.json"):
        print("Error: shanghaitech_personnel_master.json not found!")
        return

    with open("shanghaitech_personnel_master.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # course_name -> list of grade points/marks
    course_marks = defaultdict(list)
    # course_name -> list of overall GPAs of students enrolled
    course_student_gpas = defaultdict(list)
    # course_name -> dict of mark distribution { "4.0": count, "3.7": count, ... }
    course_distributions = defaultdict(lambda: defaultdict(int))
    # course_name -> course code (we try to find the code from the student records or default)
    course_codes = {}

    for person in data:
        if person.get("personnel_type") != "student":
            continue
        
        # Calculate overall student GPA
        overall_gpa = safe_float(person.get("custom_gpa"))
        if overall_gpa is None and person.get("gpa_summary"):
            try:
                gpa_sum = json.loads(person.get("gpa_summary"))
                overall_gpa = safe_float(gpa_sum.get("gpa"))
            except Exception:
                pass

        scores_str = person.get("scores")
        if not scores_str:
            continue
        
        try:
            scores_obj = json.loads(scores_str)
            score_array = scores_obj.get("scoreArray", [])
            for semester in score_array:
                for course in semester.get("value", []):
                    cname = course.get("name")
                    if not cname:
                        continue
                    
                    val = course.get("value", {})
                    ccode = val.get("code")
                    if ccode and ccode != "-":
                        course_codes[cname] = ccode
                    
                    mark_str = val.get("mark")
                    mark_flt = safe_float(mark_str)
                    
                    if mark_str:
                        # Clean mark string for distribution
                        m_key = mark_str.strip()
                        course_distributions[cname][m_key] += 1
                        
                        if mark_flt is not None:
                            course_marks[cname].append(mark_flt)
                    
                    if overall_gpa is not None:
                        course_student_gpas[cname].append(overall_gpa)
        except Exception as e:
            # Skip invalid records
            continue

    # Build final stats dictionary
    stats = {}
    for name in set(list(course_marks.keys()) + list(course_student_gpas.keys())):
        marks = course_marks[name]
        st_gpas = course_student_gpas[name]
        dist = dict(course_distributions[name])
        
        avg_mark = round(sum(marks) / len(marks), 3) if marks else None
        avg_student_gpa = round(sum(st_gpas) / len(st_gpas), 3) if st_gpas else None
        
        stats[name] = {
            "code": course_codes.get(name, ""),
            "count": len(dist), # unique students taking it is sum(dist.values())
            "enrollments": sum(dist.values()),
            "avg_mark": avg_mark,
            "avg_student_gpa": avg_student_gpa,
            "distribution": dist
        }

    # Save stats
    with open("course_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"Success! Processed {len(stats)} courses and saved to course_stats.json.")

if __name__ == "__main__":
    main()

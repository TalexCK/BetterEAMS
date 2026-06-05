import json
import random
import re
from collections import defaultdict

def get_dept_from_code(code):
    # Map course code prefixes to departments
    if not code:
        return "公共服务"
    code = code.upper()
    if any(code.startswith(p) for p in ["CS", "EE", "SI"]):
        return "信息科学与技术学院"
    elif any(code.startswith(p) for p in ["PHYS", "CHEM", "MSE"]):
        return "物质科学与技术学院"
    elif any(code.startswith(p) for p in ["BIO", "SL", "BME"]):
        return "生命科学与技术学院"
    elif any(code.startswith(p) for p in ["ARTS", "DESIGN", "CPRA"]):
        return "创意与艺术学院"
    elif any(code.startswith(p) for p in ["ENTR", "FINA", "ECON", "MGMT", "BHSC", "QMS"]):
        return "创业与管理学院"
    elif any(code.startswith(p) for p in ["GEHA", "GELC", "GEPE", "MT"]):
        return "人文科学研究院"
    else:
        return "通识教育中心"

def get_category_from_code(code):
    code = code.upper()
    if code.startswith("GEPE"):
        return "体育课程"
    elif code.startswith("GEMA") or code.startswith("PHYS11") or code.startswith("CHEM11"):
        return "通识必修"
    elif code.startswith("GEHA") or code.startswith("GELC"):
        return "通识选修"
    elif any(code.startswith(p) for p in ["CS", "EE", "SI"]):
        # Determine level
        match = re.search(r'\d+', code)
        if match:
            num = int(match.group())
            if num < 115:
                return "专业必修"
        return "专业选修"
    elif any(code.startswith(p) for p in ["BIO", "CHEM", "PHYS", "MSE"]):
        match = re.search(r'\d+', code)
        if match:
            num = int(match.group())
            if num < 120:
                return "专业必修"
        return "专业选修"
    else:
        return "任意选修"

def generate_schedule(code, credits):
    # Deterministic random generator based on code string so it's consistent
    state = random.getstate()
    random.seed(code)
    
    # Summer/Standard periods: Monday to Friday
    # Periods: 1-2, 3-4, 5-6, 7-8, 9-10, 11-12
    days = [1, 2, 3, 4, 5]
    slots = [
        [1, 2], [3, 4], [5, 6], [7, 8], [9, 10]
    ]
    
    sched = []
    # If 4 credits: 2 slots per week (e.g. Mon 1-2, Wed 1-2)
    # If 2 or 3 credits: 1 or 2 slots
    # If 1 credit: 1 slot (2 periods)
    num_slots = 2 if credits >= 3.0 else 1
    
    selected_days = random.sample(days, num_slots)
    selected_slots = random.sample(slots, num_slots)
    
    for i in range(num_slots):
        day = selected_days[i]
        periods = selected_slots[i]
        sched.append({
            "day": day,
            "periods": periods
        })
        
    random.setstate(state)
    return sched

def generate_venue(code, dept):
    state = random.getstate()
    random.seed(code)
    
    rooms = {
        "信息科学与技术学院": ["信息学院 1A-108", "信息学院 1A-204", "信息学院 1C-101", "信息学院 2-115"],
        "物质科学与技术学院": ["物质学院 2-202", "物质学院 3-104", "物质学院 5-301"],
        "生命科学与技术学院": ["生命学院 A-106", "生命学院 B-201", "生命学院 C-102"],
        "创意与艺术学院": ["创艺学院 W-507", "创艺学院 E-405", "创艺学院 S-103"],
        "创业与管理学院": ["创管学院 205", "创管学院 209", "创管学院 102"],
        "人文科学研究院": ["教学中心 401", "教学中心 402", "教学中心 406", "教学中心 405"]
    }
    
    options = rooms.get(dept, ["教学中心 101", "教学中心 102", "教学中心 203"])
    room = random.choice(options)
    
    random.setstate(state)
    return room

def main():
    print("Loading datasets...")
    with open("undergrad_courses.json", "r", encoding="utf-8") as f:
        undergrad = json.load(f)
    with open("grad_courses.json", "r", encoding="utf-8") as f:
        grad = json.load(f)
    with open("course_stats.json", "r", encoding="utf-8") as f:
        stats = json.load(f)
    with open("shanghaitech_personnel_master.json", "r", encoding="utf-8") as f:
        personnel = json.load(f)

    # Group staff by department
    staff_by_dept = defaultdict(list)
    for p in personnel:
        if p.get("personnel_type") == "staff" and p.get("name"):
            dept = p.get("department", "通识教育中心")
            staff_by_dept[dept].append(p.get("name"))

    # Default fallback teachers if dept has none
    default_teachers = ["张建", "王敏", "李强", "赵伟"]

    all_courses = []
    
    # Combine lists
    raw_courses = []
    for c in undergrad:
        raw_courses.append((c, 'undergrad'))
    for c in grad:
        raw_courses.append((c, 'grad'))

    seen_codes = set()

    for c, ctype in raw_courses:
        code = c.get("code")
        name = c.get("name")
        credits = float(c.get("credits", 0.0))
        
        if not code or code in seen_codes:
            continue
        seen_codes.add(code)

        dept = get_dept_from_code(code)
        category = "研究生课程" if ctype == 'grad' else get_category_from_code(code)
        
        # Pick teachers
        dept_staff = staff_by_dept.get(dept, [])
        state = random.getstate()
        random.seed(code)
        if dept_staff:
            teachers = random.sample(dept_staff, min(len(dept_staff), random.choice([1, 2])))
        else:
            teachers = [random.choice(default_teachers)]
        random.setstate(state)

        schedule = generate_schedule(code, credits)
        venue = generate_venue(code, dept)
        
        # Get GPA stats
        c_stats = stats.get(name, {})
        
        all_courses.append({
            "code": code,
            "name": name,
            "credits": credits,
            "type": ctype,
            "category": category,
            "department": dept,
            "teachers": teachers,
            "schedule": schedule,
            "venue": venue,
            "stats": {
                "enrollments": c_stats.get("enrollments", 0),
                "avg_mark": c_stats.get("avg_mark", None),
                "avg_student_gpa": c_stats.get("avg_student_gpa", None),
                "distribution": c_stats.get("distribution", {})
            }
        })

    with open("courses_with_details.json", "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)

    print(f"Created courses_with_details.json with {len(all_courses)} enriched courses.")

if __name__ == "__main__":
    main()

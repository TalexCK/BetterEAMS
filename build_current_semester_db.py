import json
import re

def parse_raw_javascript_lessons(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    # The file starts with "var lessonJSONs = [" and ends with "];" or similar.
    # We want to extract the JSON array.
    # Since it's valid JS but might contain unquoted keys (e.g. {id:66203,no:'...'}), 
    # we can use a simple python evaluator or a regex parser, or we can load it by parsing Javascript.
    # To parse JavaScript object literals safely in Python, we can clean up the keys and parse as JSON,
    # or write a simple script that evaluates it or uses regex.
    # Let's write a robust parser. Since we have node/npm or python, we can write a regex-based parser
    # that converts JS object literals to standard JSON.
    
    # 1. Extract the array content between first [ and last ]
    start_idx = content.find('[')
    end_idx = content.rfind(']')
    if start_idx == -1 or end_idx == -1:
        print("Error: Could not find array boundaries in raw text.")
        return []
        
    array_content = content[start_idx:end_idx+1]
    
    # 2. Convert JS-like object to JSON:
    # - Quote unquoted keys: e.g. id: -> "id":
    # - Quote single quoted strings: 'abc' -> "abc"
    # - Remove trailing commas before } or ]
    
    # Replace single quotes with double quotes
    # (Be careful about nested quotes, but EAMS uses simple single quotes for strings)
    json_str = array_content
    
    # Match keys like id: or no: or name: (alphanumeric keys followed by colon)
    # We use regex to find word character keys followed by colon, and wrap the key in double quotes.
    json_str = re.sub(r'(\b\w+\b)\s*:', r'"\1":', json_str)
    
    # Convert single-quoted string values to double-quoted
    # e.g. '当代摄影与图像处理' -> "当代摄影与图像处理"
    # Matches single quoted strings, avoiding double quotes inside if any
    json_str = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', json_str)
    
    # Remove trailing commas before closing braces
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    # Parse standard JSON
    try:
        lessons = json.loads(json_str)
        return lessons
    except Exception as e:
        print(f"Standard JSON parse failed: {e}. Trying secondary regex extraction...")
        # Fallback regex extraction for each course object
        return parse_via_regex(array_content)

def parse_via_regex(array_content):
    # Fallback parser using regex to extract fields from each object
    # Matches {id:..., arrangeInfo:[...]}
    lessons = []
    # Split by object closures. Since EAMS format is consistent, we can find individual objects.
    # EAMS format is {id:...,arrangeInfo:[...]},{id:...,arrangeInfo:[...]}
    # We can split by "}," or regex matching object boundaries
    matches = re.finditer(r'\{id:\d+,.*?,arrangeInfo:\[.*?\]\}', array_content)
    for m in matches:
        obj_text = m.group()
        # Extract fields
        c_id = re.search(r'id:(\d+)', obj_text)
        no = re.search(r"no:['\"]([^'\"]+)['\"]", obj_text)
        name = re.search(r"name:['\"]([^'\"]+)['\"]", obj_text)
        code = re.search(r"code:['\"]([^'\"]+)['\"]", obj_text)
        credits = re.search(r'credits:([\d\.]+)', obj_text)
        teachers = re.search(r"teachers:['\"]([^'\"]*)['\"]", obj_text)
        dept = re.search(r"teachDepartName:['\"]([^'\"]*)['\"]", obj_text)
        cat = re.search(r"courseTypeName:['\"]([^'\"]*)['\"]", obj_text)
        pre = re.search(r"preRequirement:['\"]([^'\"]*)['\"]", obj_text)
        
        # Parse arrangeInfo
        arrange_text = re.search(r'arrangeInfo:\[(.*?)\]', obj_text)
        schedule = []
        venue = "未知"
        if arrange_text:
            slots_text = arrange_text.group(1)
            # Find individual slot objects like {weekDay:4,startUnit:1,endUnit:4,rooms:'创管学院205'}
            slots = re.finditer(r'\{weekDay:(\d+),.*?startUnit:(\d+),endUnit:(\d+),.*?rooms:[\'\"]([^\'\"]+)[\'\"]\}', slots_text)
            for s in slots:
                day = int(s.group(1))
                start = int(s.group(2))
                end = int(s.group(3))
                venue = s.group(4)
                schedule.append({
                    "day": day,
                    "periods": list(range(start, end + 1))
                })
        
        lessons.append({
            "id": int(c_id.group(1)) if c_id else 0,
            "no": no.group(1) if no else "",
            "name": name.group(1) if name else "",
            "code": code.group(1) if code else "",
            "credits": float(credits.group(1)) if credits else 0.0,
            "teachers": teachers.group(1).split(",") if teachers and teachers.group(1) else [],
            "department": dept.group(1) if dept else "其他院系",
            "category": cat.group(1) if cat else "任意选修",
            "preRequirement": pre.group(1) if pre else "无",
            "schedule": schedule,
            "venue": venue
        })
    return lessons

def main():
    print("Parsing EAMS raw course data...")
    lessons = parse_raw_javascript_lessons("current_semester_courses_raw.txt")
    print(f"Extracted {len(lessons)} current semester courses.")
    
    # Load GPA stats
    try:
        with open("course_stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)
    except Exception:
        stats = {}
        
    enriched_lessons = []
    for c in lessons:
        name = c.get("name")
        c_stats = stats.get(name, {})
        
        # Format category to match our sidebar tabs
        raw_cat = c.get("category", "任意选修")
        category = "任意选修"
        if "必修" in raw_cat:
            if "通识" in raw_cat or "公共" in raw_cat:
                category = "通识必修"
            else:
                category = "专业必修"
        elif "选修" in raw_cat:
            if "通识" in raw_cat:
                category = "通识选修"
            elif "专业" in raw_cat:
                category = "专业选修"
            else:
                category = "任意选修"
        elif "体育" in raw_cat:
            category = "体育课程"
        elif "研究生" in raw_cat:
            category = "研究生课程"
            
        c["category"] = category
        c["stats"] = {
            "enrollments": c_stats.get("enrollments", 0),
            "avg_mark": c_stats.get("avg_mark", None),
            "avg_student_gpa": c_stats.get("avg_student_gpa", None),
            "distribution": c_stats.get("distribution", {})
        }
        enriched_lessons.append(c)
        
    with open("current_semester_courses.json", "w", encoding="utf-8") as f:
        json.dump(enriched_lessons, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved {len(enriched_lessons)} enriched courses to current_semester_courses.json.")

if __name__ == "__main__":
    main()

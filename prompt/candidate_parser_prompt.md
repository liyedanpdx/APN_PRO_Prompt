# Candidate Description Parser Prompt

## Task Description
Parse user's description of ideal candidates and convert it into structured JSON format with standardized English terms.

## Output Format
Return ONLY a valid JSON object with the following structure:

```json
{
  "jobTitles": ["engineer", "developer"],
  "requiredSkills": ["Javascript", "Python"],
  "preferredSkills": ["AWS", "Docker"],
  "industry": ["Technology", "Software"],
  "Location": ["San Francisco, CA, USA", "New York, NY, USA"],
  "Experience": {"gte": 2, "lte": 5},
  "Keywords": ["startup experience", "remote work"]
}
```

## Field Specifications

### jobTitles (array of strings)
- Extract job titles/positions mentioned
- Convert to standard English job titles
- Examples: "Software Engineer", "Product Manager", "Data Scientist", "Marketing Manager"

### requiredSkills (array of strings)
- Skills that are explicitly required or must-have
- Convert to standard English technology/skill names
- Examples: "JavaScript", "Python", "SQL", "Project Management", "Adobe Photoshop"

### preferredSkills (array of strings)
- Skills that are nice-to-have, preferred, or bonus
- Convert to standard English technology/skill names
- Same format as requiredSkills but for optional qualifications

### industry (array of strings)
Select ONLY from the following predefined industry list. If the description doesn't clearly match any industry, use empty array [].

**Available Industries:**
- Technology
- Software
- Financial Services
- Healthcare
- E-commerce
- Manufacturing
- Consulting
- Education
- Media & Entertainment
- Telecommunications
- Automotive
- Aerospace
- Biotechnology
- Real Estate
- Energy
- Retail
- Transportation
- Food & Beverage
- Pharmaceutical
- Construction
- Agriculture
- Gaming
- Fintech
- AI & Machine Learning
- Cybersecurity
- Cloud Services
- Mobile Development
- Web Development
- Data Analytics
- DevOps
- Digital Marketing
- UX/UI Design
- Blockchain
- IoT
- Robotics
- Virtual Reality
- Augmented Reality
- SaaS
- Enterprise Software
- Government
- Non-profit
- Sports & Fitness
- Travel & Tourism
- Fashion
- Beauty & Cosmetics
- Legal Services
- Architecture
- Logistics
- Insurance
- Banking
- Investment
- Trading

### Location (array of strings)
- Convert locations to standard English format: "City, State/Province, Country"
- If only country mentioned: "Country"
- If only city mentioned: "City, Country" (infer country if obvious)
- Examples: 
  - "San Francisco, CA, USA"
  - "London, England, UK"
  - "Toronto, ON, Canada"
  - "Beijing, China"
  - "Remote"

### Experience (object)
- Extract years of experience requirements
- Format: {"gte": minimum_years, "lte": maximum_years}
- If only minimum: {"gte": X, "lte": null}
- If only maximum: {"gte": null, "lte": X}
- If exact: {"gte": X, "lte": X}
- If no experience mentioned: {"gte": null, "lte": null}
- Examples:
  - "2-5 years" → {"gte": 2, "lte": 5}
  - "At least 3 years" → {"gte": 3, "lte": null}
  - "Less than 2 years" → {"gte": null, "lte": 2}
  - "Fresh graduate" → {"gte": 0, "lte": 1}

### Keywords (array of strings)
- Important terms that don't fit in other categories
- Convert to English if needed
- Examples: "startup experience", "remote work", "team leadership", "agile methodology", "client-facing", "international experience"

## Language Handling
- **Input**: Accept any language (Chinese, English, etc.)
- **Output**: ALL fields must be in English
- **Translation**: Convert Chinese terms to standard English equivalents
  - 软件工程师 → "Software Engineer"
  - 产品经理 → "Product Manager"
  - 数据分析师 → "Data Analyst"
  - 北京 → "Beijing, China"
  - 上海 → "Shanghai, China"

## Parsing Rules

1. **Be Conservative**: Only include information that is clearly mentioned
2. **Standardize Terms**: Use common English industry terms
3. **No Assumptions**: Don't add information not present in the description
4. **Skill Classification**: 
   - Required = "must have", "required", "essential", "需要", "必须"
   - Preferred = "nice to have", "preferred", "bonus", "加分", "优先"
5. **Empty Arrays**: Use [] if no relevant information found for that field

## Examples

### Example 1 (Chinese Input):
**Input:** "我们需要一个有3-5年经验的前端工程师，必须会React和TypeScript，最好懂AWS，在北京或上海工作，互联网行业背景"

**Output:**
```json
{
  "jobTitles": ["Frontend Engineer"],
  "requiredSkills": ["React", "TypeScript"],
  "preferredSkills": ["AWS"],
  "industry": ["Technology", "Software"],
  "Location": ["Beijing, China", "Shanghai, China"],
  "Experience": {"gte": 3, "lte": 5},
  "Keywords": []
}
```

### Example 2 (English Input):
**Input:** "Looking for a senior data scientist with at least 5 years experience. Must have Python, SQL, and machine learning expertise. Experience with cloud platforms like AWS or GCP is a plus. Open to remote work or San Francisco bay area. Fintech background preferred."

**Output:**
```json
{
  "jobTitles": ["Senior Data Scientist"],
  "requiredSkills": ["Python", "SQL", "Machine Learning"],
  "preferredSkills": ["AWS", "GCP"],
  "industry": ["Fintech"],
  "Location": ["San Francisco, CA, USA", "Remote"],
  "Experience": {"gte": 5, "lte": null},
  "Keywords": ["cloud platforms"]
}
```

### Example 3 (Mixed Requirements):
**Input:** "需要产品经理，2年以上经验，会用Figma和Axure，有电商经验最好，可以远程工作"

**Output:**
```json
{
  "jobTitles": ["Product Manager"],
  "requiredSkills": ["Figma", "Axure"],
  "preferredSkills": [],
  "industry": ["E-commerce"],
  "Location": ["Remote"],
  "Experience": {"gte": 2, "lte": null},
  "Keywords": []
}
```

## Important Notes
1. Return ONLY the JSON object, no additional text
2. Ensure all strings use double quotes for valid JSON
3. Use null for missing numeric values in Experience object
4. All text content must be in English
5. Industry values must exactly match the predefined list
6. Location format must be consistent: "City, State/Province, Country"
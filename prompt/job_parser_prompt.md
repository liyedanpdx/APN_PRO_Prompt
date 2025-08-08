# Job Description Parser Prompt

## Task Description
Parse job descriptions (JD) and convert them into structured JSON format with standardized English terms.

## Output Format
Return ONLY a valid JSON object with the following structure:

```json
{
  "jobTitles": ["Software Engineer", "Backend Developer"],
  "requiredSkills": ["Javascript", "Python"],
  "preferredSkills": ["AWS", "Docker"],
  "industry": ["Technology", "Software"],
  "Location": ["San Francisco, CA, USA", "New York, NY, USA"],
  "Experience": {"gte": 2, "lte": 5},
  "Keywords": ["startup environment", "remote work"]
}
```

## Field Specifications

### jobTitles (array of strings)
- Extract job titles/positions mentioned in the JD
- Convert to standard English job titles
- Examples: "Software Engineer", "Product Manager", "Data Scientist", "Marketing Manager"

### requiredSkills (array of strings)
- Skills that are explicitly required or must-have in the job description
- Convert to standard English technology/skill names
- Examples: "JavaScript", "Python", "SQL", "Project Management", "Adobe Photoshop"

### preferredSkills (array of strings)
- Skills that are nice-to-have, preferred, or bonus qualifications
- Convert to standard English technology/skill names
- Same format as requiredSkills but for optional qualifications

### industry (array of strings)
Select ONLY from the following predefined industry list. If the job description doesn't clearly match any industry, use empty array [].

**Available Industries:**
- Abrasives and Nonmetallic Minerals Manufacturing
- Accessible Architecture and Design
- Accessible Hardware Manufacturing
- Accommodation Services
- Accounting
- Administration of Justice
- Administrative and Support Services
- Advertising Services
- Agricultural Chemical Manufacturing
- Agriculture, Construction, Mining Machinery Manufacturing
- Air, Water, and Waste Program Management
- Airlines and Aviation
- Alternative Dispute Resolution
- Alternative Fuel Vehicle Manufacturing
- Alternative Medicine
- Ambulance Services
- Amusement Parks and Arcades
- Animal Feed Manufacturing
- Animation and Post-production
- Apparel Manufacturing
- Appliances, Electrical, and Electronics Manufacturing
- Architectural and Structural Metal Manufacturing
- Architecture and Planning
- Armed Forces
- Artificial Rubber and Synthetic Fiber Manufacturing
- Artists and Writers
- Audio and Video Equipment Manufacturing
- Automation Machinery Manufacturing
- Aviation and Aerospace Component Manufacturing
- Baked Goods Manufacturing
- Banking
- Bars, Taverns, and Nightclubs
- Bed-and-Breakfasts, Hostels, Homestays
- Beverage Manufacturing
- Biomass Electric Power Generation
- Biotechnology Research
- Blockchain Services
- Blogs
- Boilers, Tanks, and Shipping Container Manufacturing
- Book Publishing
- Book and Periodical Publishing
- Breweries
- Broadcast Media Production and Distribution
- Building Construction
- Building Equipment Contractors
- Building Finishing Contractors
- Building Structure and Exterior Contractors
- Business Consulting and Services
- Business Content
- Business Intelligence Platforms
- Cable and Satellite Programming
- Capital Markets
- Caterers
- Chemical Manufacturing
- Chemical Raw Materials Manufacturing
- Child Day Care Services
- Chiropractors
- Circuses and Magic Shows
- Civic and Social Organizations
- Civil Engineering
- Claims Adjusting, Actuarial Services
- Clay and Refractory Products Manufacturing
- Climate Data and Analytics
- Climate Technology Product Manufacturing
- Coal Mining
- Collection Agencies
- Commercial and Industrial Equipment Rental
- Commercial and Industrial Machinery Maintenance
- Commercial and Service Industry Machinery Manufacturing
- Communications Equipment Manufacturing
- Community Development and Urban Planning
- Community Services
- Computer Games
- Computer Hardware Manufacturing
- Computer Networking Products
- Computer and Network Security
- Computers and Electronics Manufacturing
- Conservation Programs
- Construction
- Construction Hardware Manufacturing
- Consumer Goods Rental
- Consumer Services
- Correctional Institutions
- Cosmetology and Barber Schools
- Courts of Law
- Credit Intermediation
- Cutlery and Handtool Manufacturing
- Dairy Product Manufacturing
- Dance Companies
- Data Infrastructure and Analytics
- Data Security Software Products
- Defense and Space Manufacturing
- Dentists
- Design Services
- Desktop Computing Software Products
- Digital Accessibility Services
- Distilleries
- E-Learning Providers
- Economic Programs
- Education
- Education Administration Programs
- Electric Lighting Equipment Manufacturing
- Electric Power Generation
- Electric Power Transmission, Control, and Distribution
- Electrical Equipment Manufacturing
- Electronic and Precision Equipment Maintenance
- Embedded Software Products
- Emergency and Relief Services
- Engineering Services
- Engines and Power Transmission Equipment Manufacturing
- Entertainment Providers
- Environmental Quality Programs
- Environmental Services
- Equipment Rental Services
- Events Services
- Executive Offices
- Executive Search Services
- Fabricated Metal Products
- Facilities Services
- Family Planning Centers
- Farming
- Farming, Ranching, Forestry
- Fashion Accessories Manufacturing
- Financial Services
- Fine Arts Schools
- Fire Protection
- Fisheries
- Flight Training
- Food and Beverage Manufacturing
- Food and Beverage Retail
- Food and Beverage Services
- Footwear Manufacturing
- Footwear and Leather Goods Repair
- Forestry and Logging
- Fossil Fuel Electric Power Generation
- Freight and Package Transportation
- Fruit and Vegetable Preserves Manufacturing
- Fuel Cell Manufacturing
- Fundraising
- Funds and Trusts
- Furniture and Home Furnishings Manufacturing
- Gambling Facilities and Casinos
- Geothermal Electric Power Generation
- Glass Product Manufacturing
- Glass, Ceramics and Concrete Manufacturing
- Golf Courses and Country Clubs
- Government Administration
- Government Relations Services
- Graphic Design
- Ground Passenger Transportation
- HVAC and Refrigeration Equipment Manufacturing
- Health and Human Services
- Higher Education
- Highway, Street, and Bridge Construction
- Historical Sites
- Holding Companies
- Home Health Care Services
- Horticulture
- Hospitality
- Hospitals
- Hospitals and Health Care
- Hotels and Motels
- Household Appliance Manufacturing
- Household Services
- Household and Institutional Furniture Manufacturing
- Housing Programs
- Housing and Community Development
- Human Resources Services
- Hydroelectric Power Generation
- IT Services and IT Consulting
- IT System Custom Software Development
- IT System Data Services
- IT System Design Services
- IT System Installation and Disposal
- IT System Operations and Maintenance
- IT System Testing and Evaluation
- IT System Training and Support
- Individual and Family Services
- Industrial Machinery Manufacturing
- Industry Associations
- Information Services
- Insurance
- Insurance Agencies and Brokerages
- Insurance Carriers
- Insurance and Employee Benefit Funds
- Interior Design
- International Affairs
- International Trade and Development
- Internet Marketplace Platforms
- Internet News
- Internet Publishing
- Interurban and Rural Bus Services
- Investment Advice
- Investment Banking
- Investment Management
- Janitorial Services
- Landscaping Services
- Language Schools
- Laundry and Drycleaning Services
- Law Enforcement
- Law Practice
- Leasing Non-residential Real Estate
- Leasing Residential Real Estate
- Leather Product Manufacturing
- Legal Services
- Legislative Offices
- Libraries
- Lime and Gypsum Products Manufacturing
- Loan Brokers
- Machinery Manufacturing
- Magnetic and Optical Media Manufacturing
- Manufacturing
- Maritime Transportation
- Market Research
- Marketing Services
- Mattress and Blinds Manufacturing
- Measuring and Control Instrument Manufacturing
- Meat Products Manufacturing
- Media & Telecommunications
- Media Production
- Medical Equipment Manufacturing
- Medical Practices
- Medical and Diagnostic Laboratories
- Mental Health Care
- Metal Ore Mining
- Metal Treatments
- Metal Valve, Ball, and Roller Manufacturing
- Metalworking Machinery Manufacturing
- Military and International Affairs
- Mining
- Mobile Computing Software Products
- Mobile Food Services
- Mobile Gaming Apps
- Motor Vehicle Manufacturing
- Motor Vehicle Parts Manufacturing
- Movies and Sound Recording
- Movies, Videos and Sound
- Museums
- Museums, Historical Sites, and Zoos
- Musicians
- Nanotechnology Research
- Natural Gas Distribution
- Natural Gas Extraction
- Newspaper Publishing
- Non-profit Organizations
- Nonmetallic Mineral Mining
- Nonresidential Building Construction
- Nuclear Electric Power Generation
- Nursing Homes and Residential Care Facilities
- Office Administration
- Office Furniture and Fixtures Manufacturing
- Oil Extraction
- Oil and Coal Product Manufacturing
- Oil and Gas
- Oil, Gas, and Mining
- Online Audio and Video Media
- Online and Mail Order Retail
- Operations Consulting
- Optometrists
- Outpatient Care Centers
- Outsourcing and Offshoring Consulting
- Packaging and Containers Manufacturing
- Paint, Coating, and Adhesive Manufacturing
- Paper and Forest Product Manufacturing
- Pension Funds
- Performing Arts
- Performing Arts and Spectator Sports
- Periodical Publishing
- Personal Care Product Manufacturing
- Personal Care Services
- Personal and Laundry Services
- Pet Services
- Pharmaceutical Manufacturing
- Philanthropic Fundraising Services
- Photography
- Physical, Occupational and Speech Therapists
- Physicians
- Pipeline Transportation
- Plastics Manufacturing
- Plastics and Rubber Product Manufacturing
- Political Organizations
- Postal Services
- Primary Metal Manufacturing
- Primary and Secondary Education
- Printing Services
- Professional Organizations
- Professional Services
- Professional Training and Coaching
- Public Assistance Programs
- Public Health
- Public Policy Offices
- Public Relations and Communications Services
- Public Safety
- Racetracks
- Radio and Television Broadcasting
- Rail Transportation
- Railroad Equipment Manufacturing
- Ranching
- Ranching and Fisheries
- Real Estate
- Real Estate Agents and Brokers
- Real Estate and Equipment Rental Services
- Recreational Facilities
- Regenerative Design
- Religious Institutions
- Renewable Energy Equipment Manufacturing
- Renewable Energy Power Generation
- Renewable Energy Semiconductor Manufacturing
- Repair and Maintenance
- Research Services
- Residential Building Construction
- Restaurants
- Retail
- Retail Apparel and Fashion
- Retail Appliances, Electrical, and Electronic Equipment
- Retail Art Dealers
- Retail Art Supplies
- Retail Books and Printed News
- Retail Building Materials and Garden Equipment
- Retail Florists
- Retail Furniture and Home Furnishings
- Retail Gasoline
- Retail Groceries
- Retail Health and Personal Care Products
- Retail Luxury Goods and Jewelry
- Retail Motor Vehicles
- Retail Musical Instruments
- Retail Office Equipment
- Retail Office Supplies and Gifts
- Retail Pharmacies
- Retail Recyclable Materials & Used Merchandise
- Reupholstery and Furniture Repair
- Robot Manufacturing
- Robotics Engineering
- Rubber Products Manufacturing
- Satellite Telecommunications
- Savings Institutions
- School and Employee Bus Services
- Seafood Product Manufacturing
- Secretarial Schools
- Securities and Commodity Exchanges
- Security Guards and Patrol Services
- Security Systems Services
- Security and Investigations
- Semiconductor Manufacturing
- Services for Renewable Energy
- Services for the Elderly and Disabled
- Sheet Music Publishing
- Shipbuilding
- Shuttles and Special Needs Transportation Services
- Sightseeing Transportation
- Skiing Facilities
- Smart Meter Manufacturing
- Soap and Cleaning Product Manufacturing
- Social Networking Platforms
- Software Development
- Solar Electric Power Generation
- Sound Recording
- Space Research and Technology
- Specialty Trade Contractors
- Spectator Sports
- Sporting Goods Manufacturing
- Sports Teams and Clubs
- Sports and Recreation Instruction
- Spring and Wire Product Manufacturing
- Staffing and Recruiting
- Steam and Air-Conditioning Supply
- Strategic Management Services
- Subdivision of Land
- Sugar and Confectionery Product Manufacturing
- Surveying and Mapping Services
- Taxi and Limousine Services
- Technical and Vocational Training
- Technology, Information and Internet
- Technology, Information and Media
- Telecommunications
- Telecommunications Carriers
- Telephone Call Centers
- Temporary Help Services
- Textile Manufacturing
- Theater Companies
- Think Tanks
- Tobacco Manufacturing
- Translation and Localization
- Transportation Equipment Manufacturing
- Transportation Programs
- Transportation, Logistics, Supply Chain and Storage
- Travel Arrangements
- Truck Transportation
- Trusts and Estates
- Turned Products and Fastener Manufacturing
- Urban Transit Services
- Utilities
- Utilities Administration
- Utility System Construction
- Vehicle Repair and Maintenance
- Venture Capital and Private Equity Principals
- Veterinary Services
- Vocational Rehabilitation Services
- Warehousing and Storage
- Waste Collection
- Waste Treatment and Disposal
- Water Supply and Irrigation Systems
- Water, Waste, Steam, and Air Conditioning Services
- Wellness and Fitness Services
- Wholesale
- Wholesale Alcoholic Beverages
- Wholesale Apparel and Sewing Supplies
- Wholesale Appliances, Electrical, and Electronics
- Wholesale Building Materials
- Wholesale Chemical and Allied Products
- Wholesale Computer Equipment
- Wholesale Drugs and Sundries
- Wholesale Food and Beverage
- Wholesale Footwear
- Wholesale Furniture and Home Furnishings
- Wholesale Hardware, Plumbing, Heating Equipment
- Wholesale Import and Export
- Wholesale Luxury Goods and Jewelry
- Wholesale Machinery
- Wholesale Metals and Minerals
- Wholesale Motor Vehicles and Parts
- Wholesale Paper Products
- Wholesale Petroleum and Petroleum Products
- Wholesale Photography Equipment and Supplies
- Wholesale Raw Farm Products
- Wholesale Recyclable Materials
- Wind Electric Power Generation
- Wineries
- Wireless Services
- Women's Handbag Manufacturing
- Wood Product Manufacturing
- Writing and Editing
- Zoos and Botanical Gardens

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
  - "Entry level" → {"gte": 0, "lte": 2}
  - "Senior level" → {"gte": 5, "lte": null}

### Keywords (array of strings)
- Important terms from the job description that don't fit in other categories
- Convert to English if needed
- Examples: "startup environment", "remote work", "team leadership", "agile methodology", "client-facing", "international team"

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

1. **Be Conservative**: Only include information that is clearly mentioned in the JD
2. **Standardize Terms**: Use common English industry terms
3. **No Assumptions**: Don't add information not present in the job description
4. **Skill Classification**: 
   - Required = "must have", "required", "essential", "需要", "必须", "责任要求"
   - Preferred = "nice to have", "preferred", "bonus", "加分", "优先", "加分项"
5. **Empty Arrays**: Use [] if no relevant information found for that field

## Examples

### Example 1 (Chinese Input):
**Input:** "我们正在招聘一名高级前端工程师，要求3-5年工作经验。必须熟练掌握React、Vue.js和TypeScript。如果有Node.js和AWS经验会优先考虑。工作地点在上海或北京，互联网公司背景。我们是一个快节奏的创业团队。"

**Output:**
```json
{
  "jobTitles": ["Senior Frontend Engineer"],
  "requiredSkills": ["React", "Vue.js", "TypeScript"],
  "preferredSkills": ["Node.js", "AWS"],
  "industry": ["Technology", "Software"],
  "Location": ["Shanghai, China", "Beijing, China"],
  "Experience": {"gte": 3, "lte": 5},
  "Keywords": ["startup team", "fast-paced"]
}
```

### Example 2 (English Input):
**Input:** "We are looking for a Senior Data Scientist to join our fintech team. The ideal candidate should have at least 5 years of experience in data science and machine learning. Requirements: Python, SQL, machine learning frameworks (TensorFlow or PyTorch). Nice to have: experience with cloud platforms like AWS or GCP, knowledge of financial markets. This is a remote-friendly position based in San Francisco bay area. We offer competitive salary and equity."

**Output:**
```json
{
  "jobTitles": ["Senior Data Scientist"],
  "requiredSkills": ["Python", "SQL", "Machine Learning", "TensorFlow", "PyTorch"],
  "preferredSkills": ["AWS", "GCP", "Financial Markets"],
  "industry": ["Fintech"],
  "Location": ["San Francisco, CA, USA", "Remote"],
  "Experience": {"gte": 5, "lte": null},
  "Keywords": ["competitive salary", "equity"]
}
```

### Example 3 (Mixed Requirements):
**Input:** "岗位：产品经理\n职责：负责产品规划和用户体验设计\n要求：\n- 2年以上产品经理经验\n- 熟练使用Figma、Axure等工具\n- 有电商或金融行业经验者优先\n- 可接受远程办公\n- 良好的英语沟通能力"

**Output:**
```json
{
  "jobTitles": ["Product Manager"],
  "requiredSkills": ["Product Planning", "UX Design", "Figma", "Axure", "English Communication"],
  "preferredSkills": [],
  "industry": ["E-commerce", "Financial Services"],
  "Location": ["Remote"],
  "Experience": {"gte": 2, "lte": null},
  "Keywords": []
}
```

### Example 4 (Complex JD):
**Input:** "Backend Software Engineer - Full Stack Team\n\nWe're seeking an experienced backend engineer to build scalable microservices for our e-commerce platform. \n\nRequired:\n- 3+ years backend development experience\n- Strong in Java, Spring Boot, and REST APIs\n- Experience with MySQL and Redis\n- Familiarity with Docker and Kubernetes\n\nPreferred:\n- AWS/GCP cloud experience\n- Message queues (RabbitMQ, Kafka)\n- CI/CD pipeline experience\n\nLocation: New York office or remote within US\nCompany: High-growth e-commerce startup"

**Output:**
```json
{
  "jobTitles": ["Backend Software Engineer"],
  "requiredSkills": ["Java", "Spring Boot", "REST API", "MySQL", "Redis", "Docker", "Kubernetes"],
  "preferredSkills": ["AWS", "GCP", "RabbitMQ", "Kafka", "CI/CD"],
  "industry": ["E-commerce", "Software"],
  "Location": ["New York, NY, USA", "Remote"],
  "Experience": {"gte": 3, "lte": null},
  "Keywords": ["microservices", "scalable", "high-growth startup"]
}
```

## Important Notes
1. Return ONLY the JSON object, no additional text
2. Ensure all strings use double quotes for valid JSON
3. Use null for missing numeric values in Experience object
4. All text content must be in English
5. Industry values must exactly match the predefined list
6. Location format must be consistent: "City, State/Province, Country"
7. Focus on extracting information that is explicitly stated in the job description
8. Don't infer or assume information that is not clearly mentioned
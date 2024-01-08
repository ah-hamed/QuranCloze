import json, csv

JSON_file = open('inputs/pages_processed.json', 'r', encoding='utf-8-sig')

pages_processed = json.load(JSON_file, strict=False)

# Prepare the index_surahs
index_surahs_csv_reader = csv.DictReader(open('inputs/index_surahs.csv', 'r', encoding='utf-8-sig'))
index_surahs = {}
for row in index_surahs_csv_reader:
    page = int(row['page'])
    if str("%03d" %page) not in index_surahs.keys():
        index_surahs[str("%03d" %page)] = []
    index_surahs[str("%03d" %page)].append({
        'name': row['name'],
        'number': row['number']
    })

# Prepare the index_ajzaa
index_ajzaa_csv_reader = csv.DictReader(open('inputs/index_ajzaa.csv', 'r'), delimiter='\t')
index_ajzaa = {}
for row in index_ajzaa_csv_reader:
    index_ajzaa[row['page']] = row['juz']

# Prepare CSV to be imported in Anki
imp_csv_file = open('outputs/importMeInAnki.csv', 'w', encoding='utf-8-sig')    
imp_csv_writer = csv.writer(imp_csv_file)

# Prepare JSON to be published
pub_fields = {}

# Prepare CSV fields
for key in pages_processed.keys():
    
    PageNumber = key

    Question = pages_processed[key]
    
    # Determine whether the page is right or left
    pagenumber = int(PageNumber)
    side = 'left' if pagenumber % 2 == 0 else 'right'

    # Calculate the starting and ending context page
    start = pagenumber - 4 if side == 'right' else pagenumber - 5
    end = pagenumber + 4 if side == 'left' else pagenumber + 5
    if pagenumber < 5:
        start = 1
    if pagenumber > 600:
        end = 604

    # Prepare "Context" field
    Context = ''
    for i in range(start, end, 2):
        Context += \
f"""<div class="flex-container">
        <div class="right_contextpage{'" id="current_contextpage"' if i == pagenumber else ''}">
            {pages_processed[str("%03d" %i)]}
        </div>
        <div class="left_contextpage{'" id="current_contextpage"' if i+1 == pagenumber else ''}">
            {pages_processed[str("%03d" %(i+1))]}
        </div>
    </div>
</div>
"""
    # Prepare "Tags"
    juz_tag = "QuranCloze::الأجزاء::الجزء_" + "%02d" %int(index_ajzaa[str(pagenumber)])
    if PageNumber in index_surahs.keys():
        surah_tag = ''
        for surah in index_surahs[PageNumber]:
            surah_tag += f'QuranCloze::السور::{"%03d" %int(surah["number"])}_سورة_{surah["name"]} ' 
    Tags = juz_tag + " " + surah_tag

    imp_csv_writer.writerow([PageNumber, Question, Context, Tags])
    
    pub_fields[pagenumber] = {
        'Question': Question,
        'Context': Context
    }

json.dump(pub_fields,
           open('outputs/pub_fields.json', 'w', encoding='utf-8-sig'),
            ensure_ascii=False)
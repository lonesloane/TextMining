# coding=utf-8

import random

random_topics = random.sample(xrange(1, 50), 15)

relevance_sample = ['normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal',
                    'normal', 'normal', 'high', 'high', 'high']

enrichment = ''
header = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' \
         '<enrichment>\n' \
         '	<annotation annotationDate="2015/09/25 01:46:18" annotationPlanName="Document Classification (Plan_DC)">\n' \
         '		<docID value="conv-1450564206"/>\n' \
         '		<language value="English"/>\n'
footer = '	</annotation>\n' \
         '</enrichment>'
enrichment += header

for topic in random_topics:
    rnd_relevance = relevance_sample[random.sample(xrange(0, 14), 1)[0]]
    xml_topic = '\t\t<subject label_en="lbl_en_{topic}" label_fr="lbl_fr_{topic}" relevance="{relevance}" ' \
                'uri="http://kim.oecd.org/Taxonomy/Topics#T{topic}">topic{topic} text' \
                '</subject>\n'.format(topic=topic, relevance=rnd_relevance)
    enrichment += xml_topic

enrichment += footer

print enrichment

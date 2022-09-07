from dataclasses import replace
from glob import glob
from platform import node
from time import sleep
import requests
import json
import os
import sys
import wikitextparser as wtp
import re
from pprint import pprint

FANDOM_URL_TPL="https://{}.fandom.com/wiki/{}?action=edit"
_CATEGORIES_FILTER=['character','role','location','organization','gangs','vehicle']

_MAX_DEPTH=5
_MAX_ENTRIES=700

# minimum number of description characters required for node to be added. 
_MIN_CONTENT_LENGTH=80
_SLEEP_INTERVAL_S=0.5
_CATEGORIES_TYPEMAP={'character': 'character', 
                     'location': 'location', 
                     'organization': 'faction', 
                     'gangs': 'faction',
                     'role': 'class',
                     'vehicle': 'vehicle' }

done_defs=[]
aid_nodes = []
skipped_entries=[]

class AIDNode:
    def __init__(self, name, description, type):
        self.name = name
        self.description = description
        self.type = type
        self.entry = description
        self.favorite = False
        self.genre = None
        self.tags = []
        self.isSelected = False
        self.attributes = None
        self.keys = name

def save_all():
    
    global aid_nodes
    global skipped_entries
    global done_defs

    fh = open('worldinfo.{}.json'.format(sys.argv[1]),'w+')
    fh.write(json.dumps(aid_nodes, indent=2))
    fh.close()

    fh = open("unprocessed.json",'w+')
    fh.write(json.dumps(skipped_entries,indent=2))
    fh.close()

    fh = open("processed.json","w+")
    fh.write(json.dumps(done_defs,indent=2))
    fh.close()

def load_processed():
    global done_defs
    fh = open("processed.json","r")
    done_defs = json.loads(fh.read())
    fh.close()





def extract_infos(sections):

    descr = re.search(r'\n\n(.*)\n\n', sections[0].plain_text(), re.S )
    if (descr != None):

        content = re.sub('<[^>]+>', '',descr.group(1).strip())
        print('=================')
        print(content)
        print('=================')
        return content

    return ''



def extract_mediawiki_data(term:str, depth=0):
    
    global done_defs
    global aid_nodes
    global skipped_entries

    ct = requests.get(FANDOM_URL_TPL.format(sys.argv[1],term))
    try:
        wiki_content = re.search(r'<textarea (.*?)>(.*)<\/textarea>', ct.text, re.S).group(2)
        parsed = wtp.parse(wiki_content)
    except:
        return

    for tpl in parsed.templates:

        if 'infobox' not in tpl.name.lower():
            continue

        tplname = tpl.name.lower().strip().replace('infobox ','').replace('infobox_','')

        if tplname not in _CATEGORIES_FILTER:
            print('[INFO] Node category {} does not seem to have directly relevent informations'.format(tplname))
            skipped_entries.append({"term": term, "cat": tplname})
        else:
            print('[INFO] Node category {} has information that must be extracted'.format(tplname))

            node_descr = extract_infos(parsed.sections)
            node_type = tplname
            if ( tplname in _CATEGORIES_TYPEMAP.keys() ):
                node_type = _CATEGORIES_TYPEMAP[tplname]
            else:
                print("[WARNING] Category {} not mapped to AIDungeon node type".format(tplname))
            
            if (len(node_descr) < _MIN_CONTENT_LENGTH):
                print('[WARNING] node description is too small for node {} to be added'.format(tplname))
            elif len(aid_nodes) < _MAX_ENTRIES:    
                aid_nodes.append(AIDNode(term.replace('_',' '), node_descr, node_type).__dict__)
                save_all()
            else:
                print('[WARNING] MAX_ENTRIES reached, quitting program !')
                sys.exit(1)


    print("[DEBUG] Wikilinks found: {}".format(len(parsed.wikilinks)))

    if (depth == _MAX_DEPTH):
        print("[WARNING] Maximum Depth reached, skipping page entries")
        return

    for link in parsed.wikilinks:
        rlink = link.title.replace(' ','_')

        if ('File:' in rlink or 'ikipedia:' in rlink or 'w:c:' in rlink):
            print('[DEBUG] Skipping link ' + rlink) 
            continue

        if rlink not in done_defs:
            print('[DEBUG] going to definition ' + rlink)
            done_defs.append(rlink)
            sleep(_SLEEP_INTERVAL_S)
            extract_mediawiki_data(rlink,depth+1)

if __name__ == "__main__":

    if (os.path.exists('processed.json')):
        load_processed()

    extract_mediawiki_data(sys.argv[2])


    




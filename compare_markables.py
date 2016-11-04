import sys
import os, os.path
from lxml import etree
import collections
import re

list_markables_att = {}

"""
read the file with the name of the attributes per markables
"""

def read_class_att(filename):
    global list_markables_att

    fileObj = open(filename, "r")
    for line in fileObj:
        line = line.rstrip('\n')
        if not re.match('^$',line) and not re.match('^#',line):
            elts = re.split('\t',line)
#            print(elts)
            if len(elts) >= 2:
                eltName = elts[0]
                temp = []
                if not elts[1] == "":
                    for i in range(1, len(elts)):
                        temp.append(elts[i])
                        list_markables_att[eltName] = temp

    fileObj.close()

"""
read files from annotator1 and annotator2 and merge them in output folder
"""

def merge_data(anno1f, anno2f, outfile):
    global list_markables_att

    anno1doc = etree.parse(anno1f, etree.XMLParser(remove_blank_text=True))
    anno1doc_root = anno1doc.getroot()
    anno1doc_root.getchildren()

    store_token_anno1 = collections.defaultdict(list)
    store_annotation_anno1 = collections.defaultdict(list)
    store_markable_attribute_anno1 = collections.defaultdict(list)

    for elem in anno1doc_root.findall("token"):
        store_token_anno1[elem.attrib.get('sentence', 'null')].append(elem.attrib.get('sentence', 'null') + "\t" + elem.text + "\t" + elem.attrib.get('t_id', 'null') + "\t" + elem.attrib.get('number', 'null'))

    for elem in anno1doc_root.find("Markables"):
        tag_name_anno1 = elem.tag
        for i in elem.getchildren():
            store_annotation_anno1[elem.attrib.get('m_id', 'null') + "\t" + tag_name_anno1].append(i.attrib.get('t_id', 'null'))
        if tag_name_anno1 in list_markables_att:
            for m in list_markables_att[tag_name_anno1]:
                store_markable_attribute_anno1[elem.attrib.get('m_id', 'null') + "\t" + tag_name_anno1].append(m + "\t" + elem.attrib.get(m, ''))


    anno2doc = etree.parse(anno2f, etree.XMLParser(remove_blank_text=True))
    anno2doc_root = anno2doc.getroot()
    anno2doc_root.getchildren()

    store_token_anno2 = collections.defaultdict(list)
    store_annotation_anno2 = collections.defaultdict(list)
    store_markable_attribute_anno2 = collections.defaultdict(list)


    for elem in anno2doc_root.findall("token"):
        store_token_anno2[elem.attrib.get('sentence', 'null')].append(elem.attrib.get('sentence', 'null') + "\t" +
            elem.text + "\t" + elem.attrib.get('t_id', 'null') + "\t" + elem.attrib.get('number', 'null'))

    for elem in anno2doc_root.find("Markables"):
        tag_name_anno2 = elem.tag
        for i in elem.getchildren():
            store_annotation_anno2[elem.attrib.get('m_id', 'null') + "\t" + tag_name_anno2].append(
                i.attrib.get('t_id', 'null'))
        if tag_name_anno2 in list_markables_att:
            for m in list_markables_att[tag_name_anno2]:
                store_markable_attribute_anno2[elem.attrib.get('m_id', 'null') + "\t" + tag_name_anno2].append(
                m + "\t" + elem.attrib.get(m, ''))

    """
    new sentence ids
    """

    token_anno1_new = {}

    for k, v in store_token_anno1.items():
        if int(k) == 0:
            token_anno1_new[int(k)] = v
        else:
            new_k = int(k) + 1
            token_anno1_new[new_k] = v


    token_anno2_new = {}

    for k, v in store_token_anno2.items():
        if int(k) == 0:
            new_k = int(k) + 1
            token_anno2_new[new_k] = v
        else:
            new_k = int(k) + 2
            token_anno2_new[new_k] = v


    token_anno1_new.update(token_anno2_new)

    c = collections.OrderedDict(sorted(token_anno1_new.items()))

    counter = 0

    """
    i = original_sentence_id; token_string; token_id, sentence_token_id
    """
    updated_tokens = collections.defaultdict(list)
    for k, v in c.items():
        for i in v:
            counter += 1
#            print(str(k), str(counter), i)
            updated_tokens[k].append(str(counter) + "\t" + i) # first element of i now is the new token id


    """
    update token-markables
    anno1 sentence = even numbers
    anno2 sentence = odd numbers
    """

    counter1 = 0
    anno1_markables_update = collections.defaultdict(list)
    anno2_markables_update = collections.defaultdict(list)

    for k, v in updated_tokens.items():
        if k%2 == 0:
            for i in range(0, len(v)):
                val = v[i]
                val_splitted = val.split("\t")
                new_tid = val_splitted[0]
                sentenceid = val_splitted[1]
                string = val_splitted[2]
                original_tid = val_splitted[3]
                sentence_number = val_splitted[4]

                for k1, v1 in store_annotation_anno1.items():
                    k1_splitted = k1.split("\t")
                    markable_label = k1_splitted[1]
                    counter1 += 1
                    if original_tid in v1:
#                        print(k,new_tid,string,sentence_number,markable_label,k1_splitted[0])
                        anno1_markables_update[str(k) + "\t" + k1].append(new_tid)
        else:
            for i in range(0, len(v)):
                val = v[i]
                val_splitted = val.split("\t")
                new_tid = val_splitted[0]
                sentenceid = val_splitted[1]
                string = val_splitted[2]
                original_tid = val_splitted[3]
                sentence_number = val_splitted[4]

                for k1, v1 in store_annotation_anno2.items():
                    k1_splitted = k1.split("\t")
                    markable_label = k1_splitted[1]
                    counter1 += 1
                    if original_tid in v1:
                        anno2_markables_update[str(k) + "\t" + k1].append(new_tid)



    """
    print output
    """

    for elem in anno1doc_root.iter():
        if elem.tag == "token":
            elem.getparent().remove(elem)

    for elem in anno1doc_root.iter():
        if elem.tag == "Markables":
            elem.getparent().remove(elem)

#    for elem in anno1doc_root.iter():
#        if elem.tag == "Relations":
#            elem.getparent().remove(elem)


                #    for elem in anno1doc_root.find("token"):
#        token.remove(elem)

    for k, v in updated_tokens.items():
        for i in range(0, len(v)):
            val = v[i]
            val_splitted = val.split("\t")
            new_tid = val_splitted[0]
            sentenceid = val_splitted[1]
            string = val_splitted[2]
            original_tid = val_splitted[3]
            sentence_number = val_splitted[4]
            t =  etree.Element("token")
            t.set('t_id', new_tid)
            t.set('sentence', str(k))
            t.set('number', sentence_number)
            t.text = string
            anno1doc_root.append(t)


    markable = etree.Element("Markables")

    counter2 = 0
    for k, v in anno1_markables_update.items():
        counter2 += 1
        tag = etree.Element(k.split("\t")[2])
        tag.set("m_id", str(counter2))

        get_attributes_anno1 = k.split("\t")[1] + "\t" + k.split("\t")[2]
        if get_attributes_anno1 in store_markable_attribute_anno1:
            for i in store_markable_attribute_anno1[get_attributes_anno1]:
                tag.set(i.split("\t")[0], i.split("\t")[1])

        for i in v:
            token_markable = etree.SubElement(tag, "token_anchor")
            token_markable.set('t_id', i)

            anno1doc_root.append(markable)
            markable.append(tag)


    counter3 = counter2
    for k, v in anno2_markables_update.items():

        counter3 += 1
        tag = etree.Element(k.split("\t")[2])
        tag.set("m_id", str(counter3))

        get_attributes_anno2 = k.split("\t")[1] + "\t" + k.split("\t")[2]
        if get_attributes_anno2 in store_markable_attribute_anno2:
            for i in store_markable_attribute_anno2[get_attributes_anno2]:
                tag.set(i.split("\t")[0], i.split("\t")[1])

        for i in v:
            token_markable = etree.SubElement(tag, "token_anchor")
            token_markable.set('t_id', i)

            anno1doc_root.append(markable)
            markable.append(tag)


    output = open(outfile, "w")
    anno1doc.write(outfile,
                    pretty_print=True,
                    xml_declaration=True,
                    encoding='utf-8')
    output.close()


#    for k, v in store_annotation_anno1.items():
#        print(v)





def run_compare(anno1dir, anno2dir, mergedir, attr_list):
    for f in os.listdir(anno1dir):
        anno2file = anno2dir + f

        if f.endswith(".xml"):
            outfile = mergedir + f
            read_class_att(attr_list)
            merge_data(anno1dir + f, anno2file, outfile)
        else:
            print("File is missing" + f)








def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 5:
        print('Usage: python compare_frames.py anno1_folder anno2_folder merge_folder attr_list')

    else:
        run_compare(argv[1], argv[2], argv[3], argv[4])


if __name__ == '__main__':
    main()
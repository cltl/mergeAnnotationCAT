# mergeAnnotationCAT
Script to merge files annotated from different annotators (on the same task) to better explore (dis-)agreements using the <a href="https://dh.fbk.eu/resources/cat-content-annotation-tool">CAT Tool</a>

The script works as follows:

python compare_markables.py folder_data_anno1 folder_data_anno2 output_folder list_attributes

The list_attributes files contains the set of attributes associated with every markable.
Once the merged annotation files are created, you can upload them in the CAT Tool, selecting the corresponding annotation task, and immediatedly compare the annotations.

The script is compatible with Python 3.x. This version of the script only merges annotations for markables, annotations concerning relations are not addressed at this stage. 

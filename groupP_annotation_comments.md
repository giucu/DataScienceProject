annotation id - itu credentials
a1 - senb
a2 - gicu
a3 - alji
a4 - lorl
a5 - mapop


a1 comments:

* Some of the images were hard to discern. For example, PAT_1547_1876_839 doesn't seem to show any clearly defined lesion, but rather a broader area of skin irritation. PAT_1051_220_356 was also hard to annotate for the same reason, hard to see where the lesion begins and ends.
* How closely should the mask fit the lesion? How much "padding" is ideal? 


a2 comments:

* Difficult to identify the concrete contraints for which parts of the skin surrounding a lesion are important enough to be highlighted in the mask. Mainly an issue of balance between  smaller masks lacking enough reference ‘ground truth’ for the program to refer and be compared to, and larger masks presenting overly vague informatio which makes each label less meaningful and precise.
* Additionally many images come with lesions that could be masked in multiple separated regions. However, since the metadata states a single diagnosis for each image, should the annotator just focus on highlighting the main area to avoid possible overcomplications when using the mask?

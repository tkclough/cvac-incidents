# cvac-incidents
I volunteer at the Chappaqua Volunteer Ambulance Corps. One of the tasks I sometimes do is download excel data from the website, and annotate it with various extra columns like time of day and type of call (cardiac, fall/injuries etc.). This was a tedious process that took around an hour to do by hand. 

This prototype automates downloading the data, annotating the table with new columns, and generating an new excel file with graphs. The type of call classifier uses an XGBClassifier with some NLTK text preprocessing. It has an accuracy ~75%, which is not good enough, but is a big step towards automation.

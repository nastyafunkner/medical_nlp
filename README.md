# medical_nlp
The project includes 2 modules for processing natural language medical records **in Russian** based on syntax parsing and labeled datasets.

More information can be found here https://github.com/nastyafunkner/medical_text_nlp_web/wiki

**1. Negations Detection Module**

Functionality:

*  Search of negated expression
*  Search of negated entity

**2. Time Expression Detection Module**

Functionality:

* Search of time expression
* Search of connected event
* Detection of uncertainty
* Normalization

**3.Datasets**
 
* tain_time.csv and test_time.csv - train test datasets for Time Expression Detection Module based on data from Almazov center and Cardiology Research Institute.
* tain_neg.csv and test_neg.csv - train test datasets for Negations Detection Module based on data from Almazov center.
* wheather_data.csv - dataset for Time Expression Detection Module based on data from https://github.com/Koziev/chatbot/tree/master/data. It contains information about weather conditions and It can be used to extend the functionality of the module to work not only on medical data.

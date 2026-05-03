# SEMANTIC_ZOOM

**SEMANTIC_ZOOM** is a web application built with [Python Flask](https://flask.palletsprojects.com/en/stable/) and the JavaScript library [D3.js](https://d3js.org) for visualizing event logs while preserving privacy constraints.

Privacy is achieved by abstracting the attributes of events in the event log. Events that originally had different attribute values can be generalized to a shared, abstracted value. This allows the transformed event log to satisfy constraints such as *k-anonymity* and *l-diversity*, reducing the risk of re-identification.

Users can express their interests in specific parts of the event log. If the defined privacy constraints are still satisfied, the abstraction level of selected attributes is reduced, providing a more detailed view of relevant events.



## Installation
1. Clone the project
```
git clone git@github.com:ColsR/SEMANTIC_ZOOM.git
cd SEMANTIC_ZOOM
```
2. Create a new virtual environment and activate the virtual environemnt
```
python -m venv venv # creation
source venv/bin/activate # activation
```
3. Install the necessary requirements 
```
pip install -r requirements/requirements.txt
```

---

## Usage 

### Run the Application
1. Activate the virtual environment
```
python -m venv [namevenv] 
```
2. Execute the program  with `flask --app webapp run` (optional: add `--port 8000` and/or  `--debug`)
3. Run the program over the URL `http://127.0.0.1:5000/` (adapt port number `5000` if necessary)

### Import an Event-Log 
Start by Import an Evnet-Log in the **Data Import & Attributes** section
* *Choose File*: Select an Event-Log from your file system. Only **.xes** Files are supported.
* *Import Event Log*: uploads the selected File.

After the Upload the **Attributes** of the Event-Log are displayed with their automatic generated **Attribute-Type**. Adjust the Attrbiute-Type in the Dropdown if necessary. 
* *Finish Configuration*: Finishs the Configuration and closes the Data Import & Attributes Section. 

### Navigate and Zoom in the Event-Log
By default the Event-Log ist absrtacted completely and only one Event is displayed in the plot. 
* Select the desired Attributes you want to use as **axis**.
* Reduce the Abstraction in the **Base Abstractions** Configuration on the right side by adjusting the slider for the desired attributes. 
This Zooms in the Attribute and if selected as an Axis the one Event will be split up to multiple Events providing an more-detailed View concerning the Attribute, which is now less abstracted.

* **Hover over an Event** for retrieving Information about Attributes of an event which are not represented in one of the axis 

After selecting the Base Abstraction it is possible to fine-tune the Zooming with **Specific Zoom** located at the bottom.
1. Select for which Attribute you want to gather more Information *(Target Column)*
2. Select under the conition of which Attribute *(Source Column)* the specific Zoom should be applied.
3. Select the *Filter Value* building the condition in the *Source Column*
4. Use the Slider to select the *Abstraction Function* 

Events which have for the *Source Column* the *Filter Value* will abstract their *Target Column* Attribute to the *Abstraction Function* Level. 

*Example: In general all timestamps are abstracted to be month precisely. Now a Specific Zoom can be applied so for all Events which have "check" as Activity the timestamp should be abstracted to days*



Some logs recommended are: 
* Sepsis cases: https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460
* Road traffic fine management process: https://doi.org/10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5

### Use custom Abstractions
To define custom Abstraction e.g. for activities you can provide datastructure describing the hierarchy in the ***custom_abstractions.json*** located in *data/working_data*

The Datastructure consists of a list containing all provided hierachies.
Each Hierarchy is defiend with \
```
[
  {
    "col_name": "ATTRIBUTE_NAME",
    "abstractions": {
      "LEVEL_NAME1": {
        "hierarchy": {
          "GROUP_NAME": [
            "VALUE_1",
            "VALUE_2"
          ]
        },
        "ranking": INTEGER
      },
      "LEVEL_NAME2": {
        "hierarchy": {
          "GROUP_NAME": [
            "VALUE_1",
            "VALUE_2"
          ]
        },
        "ranking": INTEGER
      }
    }
  }
  <-- Custom Hierarchy for next Attribute --!>
]
```
### Privacy Configuration
The required **Privacy Constraints** are set through environment variables.
* **K_EVENT (int)**: the required k-anonymity on event-level 
* **K_EDGE (int)**: the required k-anonymity on edge-level
* **K_TRACE (int)**: the required k-anonymity on trace-level
* **L_DIV (int)**: the required l-diversity on attribute-level
* **SINGLE_EVENT_L_DIV (True|False)**: if l-Diversity should be enforced for the Events
* **FOlLOW_EVENT_L_DIV (True|False)**: if l-Diversity should be enforced reagarding the possible follower of an Event
* **ENFORCE_PRIVACY (True|False)**: if Privacy-Constraints should be checked and if violated stop displaying the Event-Log
* **DELETE_TRACES (True|False)**: if Traces should be deleted to meet the Privacy-Constrains again if they are initially violated
* **DECOUPLE_TRACES (True|False)**: if set True the original case structure is split up with two direct following Events each forming an artificial Trace


## Extending the Project

### Clusterers and Abstractions

To introduce a new attribute type, you need to implement a corresponding clusterer.

1. **Define the attribute type**  
   Add the new type in the [Attribute Extractor](/src/analysis/attribute_extractor.py) and extend the `extract_attribute_type_mapping` function so that relevant attributes are mapped to this type based on their values.

2. **Create a clusterer**  
   Implement a new class inheriting from [AbstractClusterer](/src/clustering/abstract_clusterer.py).

   In most cases, it is sufficient to override:
   ```python
   build_abstractions()
   ```

   This method should return a mapping of abstraction levels. Each entry maps a name of the form:

   ```
   {attribute_type}{attribute_name}_{abstraction_name}
   ```

   to an abstraction object (instance of [AbstractAbstraction](/src/clustering/abstract_abstraction.py)).

3. **Register the clusterer**  
   Add the new clusterer to the [GeneralClusterer](/src/clustering/general_clusterer.py).

---

### Custom Abstractions

If your abstraction requires custom logic, create a new class inheriting from [AbstractAbstraction](/src/clustering/abstract_abstraction.py).

- Override `apply_abstraction()` if needed
- Pass the abstraction logic (usually a function) via the constructor

If you only want to add a new abstraction level to an existing clusterer, you can simply extend the mapping returned by its `build_abstractions()` method.

---

### Handling Complex Abstractions

Some abstractions require more context than a single attribute value.

For example, the `NumericalClusterer` precomputes splitting thresholds based on the full event log to group values into classes. These thresholds are currently stored as:

```
attribute_name -> [splitting_values]
```

This is a pragmatic solution, but could be improved in the future (e.g., by storing the data within the clusterer instance instead of using static variables).

---

### Privacy Constraints

Privacy constraints are configured via environment variables.

All checks are performed on the event log stored in:

```
/data/working_data/max_zoom.xes
```

This file represents the most detailed (least abstracted) state of the event log.

Privacy checks can be integrated into the application in:

```
/src/pages.py
```

**Important:**  
Due to abstraction, multiple original values may be mapped to the same generalized value (e.g., `"*"`).  
Unlike traditional privacy analysis, this does **not** represent a single exact value, but a set of possible underlying values.

---
## TROUBLESHOOTING
** Directory problem:**
The program was only tested on macOS. On other OS, the program might have trouble finding the folders in the directories of your computer. 
Please consider adapting the `project_root` variable.

---
## Licences and dependencies

This project is distributed under the AGPLv3. It makes use of third-party Python and JavaScript packages, whose licenses are provided in the `LICENCES_thirdparty/` directory.
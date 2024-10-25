# -*- coding: utf-8 -*-
"""crash_Decision_Tree.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Vu90u422pqv81kfZGoutL123-iaFX0k6
"""

import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import graphviz
from google.colab import drive
drive.mount('/content/drive', force_remount=True)

# Load the dataset
data = pd.read_csv('/content/drive/MyDrive/crash_data/new_test_data_Oct_7.csv', header=None)
#data.columns = data.columns.astype(str).str.replace(' ', '_')  # Replace spaces in column with underscores AHS system -> AHS_System
#data.index = data.index.astype(str).str.replace(' ', '_')  # Replace spaces in rows with underscores

column_names = ['','Crash_Number','At_Intersection','Crash_Severity','Number_of_Motorized_units','First_Harmful_Event','Causal_Unit_Action','Crash_Type','serious_with_fatalities','fatalities','serious','minor','Functional_Class','Lighting','Weather','Junction','Manner_Of_Collision','Pavement','Causal_Unit_First_Event','occupants','alcohol','NHS','AHS','Surface','Day_Of_week','time_of_day','Month','Airbags','body_type','model_year','relation_to_traffic','distracted','area','pop10']
columns_to_drop = [0,1]
data = data.drop(columns=columns_to_drop)
data.columns = column_names[len(columns_to_drop):] # Adjust column names after dropping

data.columns = column_names[len(columns_to_drop):]


# Preprocess the data
data = data.replace({'?': None, 'Null value': None})
#data['Posted Speed'] = pd.to_numeric(data['Posted Speed'], errors='coerce')
#data = data.fillna(-1) # Replace null values with -1 instead of removing the entire row
#data.dropna(inplace=True) #  drop rows with any missing values
#data = data.dropna()
#data['num'] = data['num'].apply(lambda x: 1 if x > 0 else 0)


data = pd.get_dummies(data, columns=['Weather', 'Manner_Of_Collision', 'Crash_Type', 'At_Intersection', 'Junction', 'Causal_Unit_Action', 'First_Harmful_Event', 'Number_of_Motorized_units', 'serious_with_fatalities','fatalities','serious','minor', 'Lighting', 'Causal_Unit_First_Event','occupants','alcohol','NHS','AHS','Surface','Day_Of_week','time_of_day','Month','Airbags', 'body_type','model_year','relation_to_traffic','distracted','area','pop10'])  # One-hot encode categorical variables
#data = pd.get_dummies(data, columns=['pop10'])
#print(data.columns)

def group_severity(Crash_Severity):
    if Crash_Severity in ["No Apparent Injury", "Suspected Minor Injury"]:
        return "Low Severity"
    elif Crash_Severity in ["Possible Injury", "Suspected Serious Injury"]:
        return "Moderate Severity"
    elif Crash_Severity == "Fatal Injury (Killed)":
        return "High Severity"
    else:
        return None  # Handle other categories if needed

data['grouped_severity'] = data['Crash_Severity'].apply(group_severity)
#data['grouped_severity'] = data['grouped_severity'].astype('category')

# remove "Unknown" and "Died Prior to Crash" categories (and any rows with None in 'grouped_severity')
data = data[~data['Crash_Severity'].isin(["Unknown", "Died Prior to Crash"])]
data.dropna(subset=['grouped_severity'], inplace=True)

#X = data.drop('num', axis=1)
#y = data['num']

# Select features and target variable

# features
features = ['Weather_Blowing Sand/Dirt/Soil', 'Weather_Blowing Snow','Weather_Clear', 'Weather_Cloudy', 'Weather_Fog/Smog/Smoke','Weather_Freezing Rain or Freezing Drizzle','Weather_No Additional Atmospheric Conditions', 'Weather_Other','Weather_Rain', 'Weather_Severe Crosswinds', 'Weather_Sleet or Hail','Weather_Snow', 'Weather_Unknown',
            'Manner_Of_Collision_Angle','Manner_Of_Collision_Front-To-Front','Manner_Of_Collision_Front-To-Rear','Manner_Of_Collision_Not a Collision with a Motor Vehicle In-Transport','Manner_Of_Collision_Other', 'Manner_Of_Collision_Rear-To-Rear','Manner_Of_Collision_Rear-To-Side',
            'Manner_Of_Collision_Sideswipe - Opposite Direction','Manner_Of_Collision_Sideswipe - Same Direction','Manner_Of_Collision_Unknown','Crash_Type_Angle - Left Turning', 'Crash_Type_Angle - T-Bone','Crash_Type_Animal-Vehicle', 'Crash_Type_Bicycle','Crash_Type_Crash_Type', 'Crash_Type_Head-On', 'Crash_Type_Motorcycle','Crash_Type_Off-Road Vehicle', 'Crash_Type_Pedestrian',
            'Crash_Type_Rear End', 'Crash_Type_Sideswipe','Crash_Type_Single Vehicle Run-Off-Road', 'Crash_Type_Train','Crash_Type_Undetermined','area_rural','area_suburban', 'area_urban', 'At_Intersection_No','At_Intersection_Yes', 'Junction_Acceleration/Deceleration Lane','Junction_Crossover-Related', 'Junction_Driveway Access','Junction_Driveway Access Related', 'Junction_Entrance/Exit Ramp',
            'Junction_Entrance/Exit Ramp Related', 'Junction_Intersection','Junction_Intersection-Related', 'Junction_Non-Junction','Junction_Other Location Not Listed Above within an Interchange Area (Median/Shoulder/Roadside)','Junction_Railway Grade Crossing', 'Junction_Shared-Use Path or Trail','Junction_Through Roadway', 'Junction_Unknown',
            'Causal_Unit_Action_Accelerating in Road','Causal_Unit_Action_Backing Up (Other than for Parking Position)','Causal_Unit_Action_Changing Lanes','Causal_Unit_Action_Decelerating in Road','Causal_Unit_Action_Disabled or Parked in Travel Lane','Causal_Unit_Action_Entering a Parking Position','Causal_Unit_Action_Going Straight','Causal_Unit_Action_Leaving a Parking Position',
            'Causal_Unit_Action_Making a U-Turn', 'Causal_Unit_Action_Merging','Causal_Unit_Action_Negotiating a Curve','Causal_Unit_Action_No Driver Present', 'Causal_Unit_Action_Other','Causal_Unit_Action_Passing or Overtaking Another Vehicle','Causal_Unit_Action_Starting in Road',
            'Causal_Unit_Action_Stopped in Road','Causal_Unit_Action_Successful Avoidance Maneuver to a Previous Critical Event','Causal_Unit_Action_Turning Left', 'Causal_Unit_Action_Turning Right','Causal_Unit_Action_Unknown',
            'First_Harmful_Event_Boulder','First_Harmful_Event_Bridge Overhead Structure','First_Harmful_Event_Bridge Pier or Support','First_Harmful_Event_Bridge Rail (Includes Parapet)','First_Harmful_Event_Building', 'First_Harmful_Event_Cable Barrier','First_Harmful_Event_Cargo/Equipment Loss or Shift','First_Harmful_Event_Concrete Traffic Barrier',
            'First_Harmful_Event_Culvert', 'First_Harmful_Event_Curb','First_Harmful_Event_Ditch', 'First_Harmful_Event_Embankment','First_Harmful_Event_Fell/Jumped from Vehicle','First_Harmful_Event_Fence', 'First_Harmful_Event_Fire Hydrant','First_Harmful_Event_Fire/Explosion', 'First_Harmful_Event_First_Harmful_Event','First_Harmful_Event_Gas Inhalation', 'First_Harmful_Event_Ground',
            'First_Harmful_Event_Guardrail End','First_Harmful_Event_Guardrail Face','First_Harmful_Event_Immersion - Full or Partial','First_Harmful_Event_Impact Attenuator/Crash Cushion','First_Harmful_Event_Injured in Vehicle (Non-Collision)','First_Harmful_Event_Jackknife', 'First_Harmful_Event_Live Animal','First_Harmful_Event_Mail Box','First_Harmful_Event_Motor Vehicle In-Transport','First_Harmful_Event_Motor Vehicle In-Transport Strikes or is Struck by Cargo/Persons/Objects Set-In-Motion From/By Another Motor Vehicle In-Transport','First_Harmful_Event_Motor Vehicle in Motion Outside the Trafficway',
            'First_Harmful_Event_Non-Motorist on Personal Conveyance','First_Harmful_Event_Other Fixed Object','First_Harmful_Event_Other Non-Collision','First_Harmful_Event_Other Object (Not Fixed)','First_Harmful_Event_Other Post/Other Pole/Other Support','First_Harmful_Event_Other Traffic Barrier','First_Harmful_Event_Overturn/Rollover','First_Harmful_Event_Parked Motor Vehicle','First_Harmful_Event_Pavement Surface Irregularity (Ruts/Potholes/Grates/etc.)',
            'First_Harmful_Event_Pedalcycle', 'First_Harmful_Event_Pedestrian','First_Harmful_Event_Railway Vehicle','First_Harmful_Event_Ridden Animal or Animal Drawn Conveyance','First_Harmful_Event_Shrubbery', 'First_Harmful_Event_Snow Bank','First_Harmful_Event_Thrown or Falling Object','First_Harmful_Event_Traffic Sign Support','First_Harmful_Event_Traffic Signal Support',
            'First_Harmful_Event_Tree (Standing Only)','First_Harmful_Event_Unknown','First_Harmful_Event_Utility Pole/Light Support','First_Harmful_Event_Wall','First_Harmful_Event_Working Motor Vehicle','Number_of_Motorized_units_0', 'Number_of_Motorized_units_1','Number_of_Motorized_units_2', 'Number_of_Motorized_units_3','Number_of_Motorized_units_4', 'Number_of_Motorized_units_5','Number_of_Motorized_units_More than 5',
            'serious_with_fatalities_0', 'serious_with_fatalities_1','serious_with_fatalities_2', 'serious_with_fatalities_3','serious_with_fatalities_4', 'serious_with_fatalities_5','serious_with_fatalities_6', 'serious_with_fatalities_8','serious_with_fatalities_9','serious_with_fatalities_10 or More',
            'fatalities_0', 'fatalities_1', 'fatalities_2', 'fatalities_3','fatalities_4','serious_0', 'serious_1', 'serious_2', 'serious_3','serious_4', 'serious_5', 'serious_9','serious_8', 'minor_0', 'minor_1', 'minor_10 or More', 'minor_2', 'minor_3','minor_4', 'minor_5', 'minor_6', 'minor_7', 'minor_8', 'minor_9', 'Lighting_Dark - Lighted', 'Lighting_Dark - Not Lighted','Lighting_Dark - Unknown Lighting', 'Lighting_Dawn','Lighting_Daylight', 'Lighting_Dusk','Lighting_Other', 'Lighting_Unknown',
            'Causal_Unit_First_Event_Boulder','Causal_Unit_First_Event_Bridge Overhead Structure','Causal_Unit_First_Event_Bridge Pier or Support','Causal_Unit_First_Event_Bridge Rail (Includes Parapet)','Causal_Unit_First_Event_Building','Causal_Unit_First_Event_Cable Barrier','Causal_Unit_First_Event_Cargo/Equipment Loss or Shift','Causal_Unit_First_Event_Cargo/Equipment Loss or Shift (Non-Harmful)', 'Causal_Unit_First_Event_Concrete Traffic Barrier','Causal_Unit_First_Event_Cross Centerline', 'Causal_Unit_First_Event_Cross Median','Causal_Unit_First_Event_Culvert', 'Causal_Unit_First_Event_Curb','Causal_Unit_First_Event_Ditch','Causal_Unit_First_Event_Downhill Runaway','Causal_Unit_First_Event_Embankment','Causal_Unit_First_Event_Equipment Failure (Blown Tire/Brake Failure/etc.)','Causal_Unit_First_Event_Fell/Jumped from Vehicle','Causal_Unit_First_Event_Fence', 'Causal_Unit_First_Event_Fire Hydrant','Causal_Unit_First_Event_Fire/Explosion','Causal_Unit_First_Event_Gas Inhalation',
            'Causal_Unit_First_Event_Ground','Causal_Unit_First_Event_Guardrail End','Causal_Unit_First_Event_Guardrail Face','Causal_Unit_First_Event_Immersion - Full or Partial','Causal_Unit_First_Event_Impact Attenuator/Crash Cushion','Causal_Unit_First_Event_Injured in Vehicle (Non-Collision)','Causal_Unit_First_Event_Jackknife', 'Causal_Unit_First_Event_Live Animal', 'Causal_Unit_First_Event_Mail Box', 'Causal_Unit_First_Event_Motor Vehicle In-Transport', 'Causal_Unit_First_Event_Motor Vehicle In-Transport Strikes or is Struck by Cargo/Persons/Objects Set-In-Motion From/By Another Motor Vehicle In-Transport','Causal_Unit_First_Event_Motor Vehicle in Motion Outside the Trafficway','Causal_Unit_First_Event_Non-Motorist on Personal Conveyance',
            'Causal_Unit_First_Event_Not-In-Motion or Working Motor Vehicle is Struck by Motor Vehicle In-Transport','Causal_Unit_First_Event_Other Fixed Object','Causal_Unit_First_Event_Other Non-Collision','Causal_Unit_First_Event_Other Object (Not Fixed)','Causal_Unit_First_Event_Other Post/Other Pole/Other Support','Causal_Unit_First_Event_Other Traffic Barrier','Causal_Unit_First_Event_Overturn/Rollover','Causal_Unit_First_Event_Parked Motor Vehicle','Causal_Unit_First_Event_Pavement Surface Irregularity (Ruts/Potholes/Grates/etc.)','Causal_Unit_First_Event_Pedalcycle','Causal_Unit_First_Event_Pedestrian','Causal_Unit_First_Event_Railway Vehicle','Causal_Unit_First_Event_Ran Off Roadway-Left','Causal_Unit_First_Event_Ran Off Roadway-Right','Causal_Unit_First_Event_Re-Entering Roadway','Causal_Unit_First_Event_Separation of Units','Causal_Unit_First_Event_Shrubbery','Causal_Unit_First_Event_Snow Bank','Causal_Unit_First_Event_Thrown or Falling Object','Causal_Unit_First_Event_Traffic Sign Support','Causal_Unit_First_Event_Traffic Signal Support','Causal_Unit_First_Event_Tree (Standing Only)',
            'Causal_Unit_First_Event_Unknown','Causal_Unit_First_Event_Utility Pole/Light Support','Causal_Unit_First_Event_Vehicle Set in Motion','Causal_Unit_First_Event_Vehicle Went Airborne','Causal_Unit_First_Event_Wall','Causal_Unit_First_Event_Working Motor Vehicle',
            'occupants_0', 'occupants_1','occupants_10', 'occupants_2', 'occupants_3', 'occupants_4','occupants_5', 'occupants_6', 'occupants_7', 'occupants_8','occupants_9', 'occupants_More than 10','alcohol_No', 'alcohol_Yes','NHS_NHS IM Airport Terminal','NHS_NHS IM Ferry Terminal', 'NHS_NHS IM Pipeline Terminal','NHS_NHS IM Port Terminal', 'NHS_NHS Not Intermodal', 'NHS_Not NHS','NHS_Unknown', 'AHS_Road is not on the Alaska Highway System','AHS_Road is on the Alaska Highway System', 'AHS_Unknown','Surface_Dry', 'Surface_Ice/Frost','Surface_Mud/Dirt/Gravel', 'Surface_Non-Trafficway Area', 'Surface_Oil',
            'Surface_Other', 'Surface_Sand', 'Surface_Slush', 'Surface_Snow', 'Surface_Unknown', 'Surface_Water (Standing/Moving)','Surface_Wet','Day_Of_week_Friday', 'Day_Of_week_Monday', 'Day_Of_week_Saturday','Day_Of_week_Sunday', 'Day_Of_week_Thursday', 'Day_Of_week_Tuesday','Day_Of_week_Wednesday','time_of_day_10:00 AM to 10:59 AM','time_of_day_10:00 PM to 10:59 PM', 'time_of_day_11:00 AM to 11:59 AM','time_of_day_11:00 PM to 11:59 PM', 'time_of_day_12:00 AM to 12:59 AM','time_of_day_12:00 PM to 12:59 PM', 'time_of_day_1:00 AM to 1:59 AM','time_of_day_1:00 PM to 1:59 PM', 'time_of_day_2:00 AM to 2:59 AM','time_of_day_2:00 PM to 2:59 PM', 'time_of_day_3:00 AM to 3:59 AM','time_of_day_3:00 PM to 3:59 PM', 'time_of_day_4:00 AM to 4:59 AM','time_of_day_4:00 PM to 4:59 PM', 'time_of_day_5:00 AM to 5:59 AM','time_of_day_5:00 PM to 5:59 PM', 'time_of_day_6:00 AM to 6:59 AM','time_of_day_6:00 PM to 6:59 PM', 'time_of_day_7:00 AM to 7:59 AM','time_of_day_7:00 PM to 7:59 PM', 'time_of_day_8:00 AM to 8:59 AM','time_of_day_8:00 PM to 8:59 PM', 'time_of_day_9:00 AM to 9:59 AM','time_of_day_9:00 PM to 9:59 PM','Month_April','Month_August', 'Month_December', 'Month_February', 'Month_January','Month_July', 'Month_June', 'Month_March', 'Month_May','Month_November', 'Month_October', 'Month_September', 'Airbags_No', 'Airbags_Yes', 'body_type_Unknown',
            'body_type_Unlisted Style of Construction Equipment','body_type_Utility Trailer', 'body_type_Utility Vehicle','body_type_Vacuum Cleaner', 'body_type_Van', 'body_type_Van Camper','body_type_Vanette', 'body_type_Wagon-Type Trailer', 'model_year_1970', 'model_year_1971','model_year_1972', 'model_year_1973', 'model_year_1974','model_year_1975', 'model_year_1976', 'model_year_1977','model_year_1978', 'model_year_1979', 'model_year_1980','model_year_1981', 'model_year_1982', 'model_year_1983','model_year_1984', 'model_year_1985', 'model_year_1986','model_year_1987', 'model_year_1988', 'model_year_1989','model_year_1990', 'model_year_1991', 'model_year_1992','model_year_1993', 'model_year_1994', 'model_year_1995',
            'model_year_1996', 'model_year_1997', 'model_year_1998','model_year_1999', 'model_year_2000', 'model_year_2001','model_year_2002', 'model_year_2003', 'model_year_2004','model_year_2005', 'model_year_2006', 'model_year_2007','model_year_2008', 'model_year_2009', 'model_year_2010','model_year_2011', 'model_year_2012', 'model_year_2013','model_year_2014', 'model_year_2015', 'model_year_2016','model_year_2017', 'model_year_2018', 'model_year_Before 1970','model_year_Not Applicable', 'model_year_Unknown','relation_to_traffic_Gore','relation_to_traffic_In Parking Lane/Zone','relation_to_traffic_Off Roadway - Location Unknown','relation_to_traffic_On Median', 'relation_to_traffic_On Roadside','relation_to_traffic_On Roadway', 'relation_to_traffic_On Shoulder','relation_to_traffic_Outside Trafficway','relation_to_traffic_Separator', 'relation_to_traffic_Unknown', 'distracted_Manually Operating an Electronic Communication Device (Texting/Typing/Dialing)','distracted_Not Applicable', 'distracted_Not Distracted','distracted_Other Activity - Electronic Device (Navigation Device/DVD Player/etc.)','distracted_Other Inside the Vehicle (Eating/Personal Hygiene/etc.)','distracted_Outside the Vehicle (Includes Unspecified External Distractions)','distracted_Passenger','distracted_Talking on Hand-Free Electronic Device','distracted_Talking on Hand-Held Electronic Device','distracted_Unknown', 'distracted_Unknown If Distracted','pop10_94', 'pop10_945', 'pop10_95', 'pop10_96', 'pop10_97',
            'pop10_970', 'pop10_98', 'pop10_980', 'pop10_99'
            ]

X = data[features]

# target variable
y = data['grouped_severity']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# remove rows with missing values in features
X_train.dropna(inplace=True)
y_train = y_train[X_train.index]  # Align y_train with dropped rows
X_test.dropna(inplace=True)
y_test = y_test[X_test.index]  # Align y_test with dropped rows

# Define class weights
class_weights = {
    "Low Severity": 1.0,
    "Moderate Severity": 1.5,
    "High Severity": 3.0
}

# Create the decision tree classifier with class weights
clf = DecisionTreeClassifier(random_state=42, criterion= 'entropy', max_depth=10, min_samples_leaf=1, min_samples_split=2, class_weight=class_weights)
'''
# define the hyperparameter grid to search for Decision Tree including class_weight
param_grid = {
    'criterion': ['gini', 'entropy'],
    'max_depth': [None, 5, 10, 15, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'class_weight': [{'Low Severity': 1.0, 'Moderate Severity': 1.5, 'High Severity': 3.0},
                    {'Low Severity': 1.0, 'Moderate Severity': 2.0, 'High Severity': 2.5}]
}

# perform Grid Search with Cross-Validation
grid_search = GridSearchCV(estimator=clf, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Get the best hyperparameters
best_params = grid_search.best_params_
print("Best Hyperparameters:", best_params)
'''

# Train the model with the best hyperparameters
clf.fit(X_train, y_train)
#best_clf = DecisionTreeClassifier(random_state=42, **best_params)
#best_clf.fit(X_train, y_train)


# Train the decision tree classifier
#clf.fit(X_train, y_train)

# Predict
y_pred = clf.predict(X_test)
#y_pred = best_clf.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy: {:.2f}%".format(accuracy * 100))
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(y_test, y_pred)

print('\n')
print(f'Accuracy: {accuracy*100:.2f}%')
print('\nConfusion Matrix:\n', conf_matrix)
print('\nClassification Report:\n', class_report)

class_labels = y.unique()

# Feature Importance for each class
importances = clf.feature_importances_
feature_names = X.columns

# Create a DataFrame to store feature importances
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
})

# Sort the DataFrame by importance
importance_df = importance_df.sort_values(by='Importance', ascending=False)


class_labels = y.unique()
# Plot feature importances for each class
for class_label in class_labels:
    plt.figure(figsize=(10, 6))
    plt.title(f'Feature Importance for {class_label}')
    plt.bar(importance_df['Feature'][:10], importance_df['Importance'][:10])  # Show top 10 features
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Features')
    plt.ylabel('Importance')
    plt.tight_layout()
    plt.show()

print(class_labels)
'''
# Visualize
#dot_data = export_graphviz(best_clf, out_file=None, feature_names=features, class_names=['Suspected Minor Injury', 'Possible Injury', 'Suspected Serious Injury', 'No Apparent Injury', 'Fatal Injury (Killed)', 'severity'], filled=True, rounded=True, special_characters=True)
dot_data = export_graphviz(clf, out_file=None, feature_names=features, class_names=['Low Severity', 'Moderate Severity', 'High Severity'], filled=True, rounded=True, special_characters=True)
graph = graphviz.Source(dot_data)

graph
'''
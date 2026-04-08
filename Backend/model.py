import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os
import warnings

# Models
ROOM_MODEL = "room_model.pkl"
SEAT_MODEL = "seat_model.pkl"
SEAT_ENCODER = "seat_encoder.pkl"
USER_MODEL = "user_model.pkl"

# Datasets
ROOM_DATA = "Occupancy_Estimation.csv"
SEAT_DATA = "library_seat_occupancy_dataset.csv"
USER_DATA = "smart_library_data.csv"

def train_room_model():
    print("Training Room Estimation Model...")
    if not os.path.exists(ROOM_DATA):
        print(f"Dataset {ROOM_DATA} not found. Skipping room model.")
        return
        
    df = pd.read_csv(ROOM_DATA)
    # Use basic S1 features to predict Room_Occupancy_Count
    features = ['S1_Temp', 'S1_Light', 'S1_Sound', 'S5_CO2']
    if not all(col in df.columns for col in features + ['Room_Occupancy_Count']):
        print("Missing required columns in Room Data")
        return
        
    X = df[features]
    y = df['Room_Occupancy_Count']
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    with open(ROOM_MODEL, 'wb') as f:
        pickle.dump(model, f)
    print("Room Estimation Model trained and saved.")

def train_seat_model():
    print("Training Seat Availability Model...")
    if not os.path.exists(SEAT_DATA):
        print(f"Dataset {SEAT_DATA} not found. Skipping seat model.")
        return
        
    df = pd.read_csv(SEAT_DATA)
    # Expected: Occupancy_Status, Timestamp, Day_of_Week, Noise_Level_dB
    if 'Timestamp' in df.columns:
        df['hour'] = pd.to_datetime(df['Timestamp']).dt.hour
    else:
        df['hour'] = 12 # Fallback
        
    le = LabelEncoder()
    if 'Day_of_Week' in df.columns:
        df['day_encoded'] = le.fit_transform(df['Day_of_Week'])
    else:
        df['day_encoded'] = 0
        
    df['status_encoded'] = (df['Occupancy_Status'] == 'Occupied').astype(int)
    
    X = df[['hour', 'day_encoded', 'Noise_Level_dB']]
    y = df['status_encoded']
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    with open(SEAT_MODEL, 'wb') as f:
        pickle.dump(model, f)
    with open(SEAT_ENCODER, 'wb') as f:
        pickle.dump(le, f)
    print("Seat Availability Model trained and saved.")

def train_user_model():
    print("Training Smart User Satisfaction Model...")
    if not os.path.exists(USER_DATA):
        print(f"Dataset {USER_DATA} not found. Skipping user model.")
        return
        
    df = pd.read_csv(USER_DATA)
    # Features: visit_duration, books_borrowed, digital_resource_usage, app_logins
    features = ['visit_duration', 'books_borrowed', 'digital_resource_usage', 'app_logins']
    if not all(col in df.columns for col in features + ['user_satisfaction']):
        print("Missing required columns in User Data")
        return
        
    X = df[features]
    y = df['user_satisfaction']
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    with open(USER_MODEL, 'wb') as f:
        pickle.dump(model, f)
    print("User Satisfaction Model trained and saved.")

def train_all_models():
    train_room_model()
    train_seat_model()
    train_user_model()


# prediction methods
def predict_room_occupancy(temp, light, sound, co2):
    if not os.path.exists(ROOM_MODEL): 
        train_room_model()
        if not os.path.exists(ROOM_MODEL): return 0
    with open(ROOM_MODEL, 'rb') as f: model = pickle.load(f)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pred = model.predict([[temp, light, sound, co2]])
    return float(pred[0])

def predict_seat_occupancy(hour, day_of_week_str, noise):
    if not os.path.exists(SEAT_MODEL) or not os.path.exists(SEAT_ENCODER): 
        train_seat_model()
        if not os.path.exists(SEAT_MODEL): return 0.5
        
    with open(SEAT_MODEL, 'rb') as f: model = pickle.load(f)
    with open(SEAT_ENCODER, 'rb') as f: le = pickle.load(f)
    
    try:
        if day_of_week_str in le.classes_:
            day_encoded = le.transform([day_of_week_str])[0]
        else:
            day_encoded = 0
    except ValueError:
        day_encoded = 0
        
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        probs = model.predict_proba([[hour, day_encoded, noise]])
    return float(probs[0][1])

def predict_user_satisfaction(duration, books, digital_usage, logins):
    if not os.path.exists(USER_MODEL): 
        train_user_model()
        if not os.path.exists(USER_MODEL): return 3.0
        
    with open(USER_MODEL, 'rb') as f: model = pickle.load(f)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pred = model.predict([[duration, books, digital_usage, logins]])
    return float(pred[0])

if __name__ == "__main__":
    train_all_models()

import os
import pickle
import random
import string
import csv
from datetime import datetime
import threading
import time
from email.mime.text import MIMEText
import smtplib
import json


class MedicalRecordEntry:
    def __init__(self, condition, medications, allergies, timestamp):
        self.condition = condition
        self.medications = medications
        self.allergies = allergies
        self.timestamp = timestamp


class Patient:
    def __init__(self, name, access_code, condition, medications, allergies, timestamp):
        self.name = name
        self.access_code = access_code
        self.medical_records = [MedicalRecordEntry(condition, medications, allergies, timestamp)]
        self.location = None
        self.medication_reminders = []

    def add_medical_record_entry(self, record_entry):
        self.medical_records.append(record_entry)

    def update_location(self, location):
        self.location = location

    def add_medication_reminder(self, medication, frequency):
        self.medication_reminders.append({'medication': medication, 'frequency': frequency})

    def print_medication_reminders(self):
        if self.medication_reminders:
            print("Medication Reminders:")
            for reminder in self.medication_reminders:
                print(f"Medication: {reminder['medication']}, Frequency: {reminder['frequency']}")
        else:
            print("No medication reminders set.")


class HealthcareProvider:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.patients = []
        self.appointments = []
        self.education_resources = {
            'Diabetes': 'https://www.diabetes.org/diabetes',
            'Hypertension': 'https://www.heart.org/en/health-topics/high-blood-pressure',
            'Asthma': 'https://www.lung.org/lung-health-diseases/lung-disease-lookup/asthma',
            'Obesity': 'https://www.cdc.gov/obesity/index.html',
            'Heart Disease': 'https://www.nhlbi.nih.gov/health-topics/heart-disease',
            'Arthritis': 'https://www.arthritis.org/health-wellness',
            'Depression': 'https://www.nimh.nih.gov/health/topics/depression',
            'Anxiety Disorders': 'https://adaa.org/understanding-anxiety',
            'Alzheimer\'s Disease': 'https://www.alz.org/alzheimers-dementia/what-is-alzheimers',
            'Osteoporosis': 'https://www.bones.nih.gov/health-info/bone/osteoporosis/overview',
            'Chronic Kidney Disease': 'https://www.kidney.org/atoz/content/about-chronic-kidney-disease',
            'COPD': 'https://www.copdfoundation.org/What-is-COPD/Understanding-COPD/What-is-COPD.aspx',
            'Hepatitis': 'https://www.cdc.gov/hepatitis/index.htm',
            'HIV/AIDS': 'https://www.hiv.gov/hiv-basics',
            'Parkinson\'s Disease': 'https://www.parkinson.org/understanding-parkinsons',
            'Multiple Sclerosis': 'https://www.nationalmssociety.org/What-is-MS',
            'Celiac Disease': 'https://celiac.org/about-celiac-disease/what-is-celiac-disease/',
            'Fibromyalgia': 'https://www.fmcpaware.org/aboutfibromyalgia',
            'Lupus': 'https://www.lupus.org/resources/what-is-lupus',
            'Epilepsy': 'https://www.epilepsy.com/learn/about-epilepsy-basics'
        }

    def access_medical_record(self, access_code):
        for patient in self.patients:
            if patient.access_code == access_code:
                return patient
        return None

    def add_patient(self, patient):
        self.patients.append(patient)

    def save_patient_record(self, patient):
        # Serialize patient data and save to file
        patient_folder = os.path.join("medilink_data", "Patient_Records", patient.name)  # Updated path
        if not os.path.exists(patient_folder):
            os.makedirs(patient_folder)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = os.path.join(patient_folder, f"{timestamp}.json")
        with open(file_name, 'w') as f:
            json.dump(patient.to_dict(), f)

    def generate_access_code(self):
        return ''.join(random.choices(string.digits, k=10))

    def list_access_codes(self):
        if self.patients:
            print("List of Access Codes with Patient Names:")
            for patient in self.patients:
                print(f"Access Code: {patient.access_code}, Name: {patient.name}")
        else:
            print("No patients found.")

    def delete_patient_data(self, access_code):
        for patient in self.patients:
            if access_code == patient.access_code:
                self.patients.remove(patient)
                print(f"Patient data with access code {access_code} deleted.")
                return
        print("Access code not found. No patient data deleted.")

    def search_patient(self, keyword):
        found = False
        for patient in self.patients:
            if keyword.lower() in patient.name.lower():
                print(f"Patient Name: {patient.name}")
                print(f"Access Code: {patient.access_code}")
                found = True
        if not found:
            print("No patient found with the given keyword.")


class HealthLinkSystem:
    def __init__(self):
        self.providers = []
        self.staff_profiles = []
        self.appointment_reminders = {}
        self.users = {}
        self.patients = {}
        self.inventory = {}  # Add this line
        self.bed_occupancy = {}  # Add this line
        self.load_data()

        self.backup_thread = threading.Thread(target=self.periodic_backup)
        self.backup_thread.daemon = True
        self.backup_thread.start()

    def periodic_backup(self):
        while True:
            self.save_data()
            time.sleep(300)  # Save data every 5 minutes

    def load_data(self):
        if os.path.exists('patients.json'):
            with open('patients.json', 'r') as f:
                patient_data = json.load(f)
                self.patients = {}
                for name, data in patient_data.items():
                    patient = Patient(
                        name=data['name'],
                        access_code=data['access_code'],
                        condition=data['medical_records'][0]['condition'],
                        medications=data['medical_records'][0]['medications'],
                        allergies=data['medical_records'][0]['allergies'],
                        timestamp=datetime.strptime(data['medical_records'][0]['timestamp'], "%Y-%m-%d %H:%M:%S")
                    )
                    for record in data['medical_records'][1:]:
                        patient.add_medical_record_entry(MedicalRecordEntry(
                            condition=record['condition'],
                            medications=record['medications'],
                            allergies=record['allergies'],
                            timestamp=datetime.strptime(record['timestamp'], "%Y-%m-%d %H:%M:%S")
                        ))
                    self.patients[name] = patient

        self.load_staff_profiles()

    def save_data(self):
        user_data = {username: user.to_dict() for username, user in self.users.items()}
        with open('users.json', 'w') as f:
            json.dump(user_data, f)

        patient_data = {patient.name: patient.to_dict() for patient in self.patients.values()}
        with open('patients.json', 'w') as f:
            json.dump(patient_data, f)

        self.save_staff_profiles()

    def load_staff_profiles(self):
        filename = os.path.join("medilink_data", "staff_profiles.pkl")  # Updated path
        if os.path.exists(filename):
            print(f"Loading staff profiles from {filename}")
            try:
                with open(filename, 'rb') as f:
                    self.staff_profiles = pickle.load(f)
                    print("Staff profiles loaded successfully.")
            except EOFError:
                print("Staff profile file is empty or corrupted.")
                self.staff_profiles = []
            except Exception as e:
                print(f"An error occurred while loading staff profiles: {e}")
                self.staff_profiles = []
        else:
            print("Staff profile file does not exist.")
            self.staff_profiles = []

    def save_staff_profiles(self):
        filename = os.path.join("medilink_data", "staff_profiles.pkl")  # Updated path
        with open(filename, 'wb') as f:
            pickle.dump(self.staff_profiles, f)

    def load_patient_records(self):
        for root, dirs, files in os.walk(os.path.join("medilink_data", "Patient_Records")):  # Updated path
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        patient_data = json.load(f)
                        patient = Patient.from_dict(patient_data)
                        self.patients[patient.name] = patient
                        for provider in self.providers:
                            provider.add_patient(patient)

    def register_provider(self, name, password):
        provider = HealthcareProvider(name, password)
        self.providers.append(provider)
        return provider

    def create_staff_profile(self):
        name = input("Enter your name: ")
        password = input("Enter your password: ")
        self.staff_profiles.append({'name': name, 'password': password})
        print("Profile created successfully.")

    def authenticate_provider(self, name, password):
        for profile in self.staff_profiles:
            if profile['name'] == name and profile['password'] == password:
                return True
        return False

    def schedule_appointment(self, patient, date):
        self.appointment_reminders[patient.name] = date
        self.send_appointment_reminder(patient, date)

    def reschedule_appointment(self, patient, new_date):
        self.appointment_reminders[patient.name] = new_date
        self.send_appointment_reminder(patient, new_date)

    def cancel_appointment(self, patient):
        if patient.name in self.appointment_reminders:
            del self.appointment_reminders[patient.name]
            print("Appointment cancelled.")
        else:
            print("No appointment found to cancel.")

    def send_appointment_reminder(self, patient, date):
        if hasattr(patient, 'email') and patient.email:
            msg = MIMEText(f"Reminder: Your appointment is scheduled for {date}.")
            msg['Subject'] = 'Appointment Reminder'
            msg['From'] = os.getenv('HEALTHLINK_EMAIL', 'no-reply@healthlink.com')
            msg['To'] = patient.email

            smtp_server = os.getenv('SMTP_SERVER', 'smtp.example.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')

            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    if smtp_username and smtp_password:
                        server.login(smtp_username, smtp_password)
                    server.send_message(msg)
                print(f"Appointment reminder sent to {patient.email}.")
            except Exception as e:
                print(f"Failed to send appointment reminder: {str(e)}")
        else:
            print("Patient email not set. Cannot send reminder.")

    def generate_patient_report(self):
        patient_name = input("Enter patient's name: ")
        if patient_name in self.patients:
            patient = self.patients[patient_name]
            print(f"Generating patient report for {patient.name}...")
            if patient.medical_records:
                print(f"Patient Report for {patient.name}:")
                for record in patient.medical_records:
                    print(f"Condition: {record.condition}")
                    print(f"Medications: {', '.join(record.medications)}")
                    print(f"Allergies: {', '.join(record.allergies)}")
                    print(f"Timestamp: {record.timestamp}")
                    print("------------------------")
            else:
                print("No medical records found for this patient.")
        else:
            print("Patient not found. Unable to generate the report.")

    def export_patient_data(self):
        with open('patient_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Access Code', 'Condition', 'Medications', 'Allergies', 'Timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for patient in self.patients.values():
                for record in patient.medical_records:
                    writer.writerow({
                        'Name': patient.name,
                        'Access Code': patient.access_code,
                        'Condition': record.condition,
                        'Medications': ', '.join(record.medications),
                        'Allergies': ', '.join(record.allergies),
                        'Timestamp': record.timestamp
                    })

    def add_health_education_resources(self, condition, url):
        for provider in self.providers:
            provider.education_resources[condition] = url

    def view_health_education_resources(self):
        print("Health Education Resources:")
        for provider in self.providers:
            for condition, url in provider.education_resources.items():
                print(f"{condition}: {url}")

    def access_medical_record(self, access_code):
        for patient in self.patients.values():
            if patient.access_code == access_code:
                return patient
        return None

    def add_patient(self, patient):
        self.patients[patient.name] = patient
        if self.providers:
            self.providers[0].add_patient(patient)
        else:
            print("No healthcare providers registered. Cannot add patient.")

    def view_current_inventory(self):
        if self.inventory:
            print("Current Inventory:")
            for item, quantity in self.inventory.items():
                print(f"{item}: {quantity}")
        else:
            print("Inventory is empty.")

    def update_inventory(self):
        item = input("Enter item name: ")
        quantity = int(input("Enter quantity: "))
        self.inventory[item] = quantity
        print("Inventory updated successfully.")

    def view_bed_occupancy(self):
        if self.bed_occupancy:
            print("Current Bed Occupancy:")
            for ward, occupancy in self.bed_occupancy.items():
                print(f"{ward}: {occupancy}")
        else:
            print("No bed occupancy data available.")

    def update_bed_availability(self):
        ward = input("Enter ward name: ")
        occupancy = int(input("Enter current occupancy: "))
        self.bed_occupancy[ward] = occupancy
        print("Bed availability updated successfully.")

    def request_medication_refill(self, patient, medication, quantity):
        print(f"Medication refill request for {patient.name}:")
        print(f"Medication: {medication}")
        print(f"Quantity: {quantity}")
        print("Request sent to pharmacy.")

    def generate_access_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def add_medical_record(self, username, condition, medications, allergies):
        if username in self.patients:
            record = MedicalRecordEntry(condition, medications, allergies, datetime.now())
            self.patients[username].add_medical_record_entry(record)
            self.save_data()
            return True
        return False

    def add_appointment(self, username, appointment):
        if username in self.patients:
            self.patients[username].appointments.append(appointment)
            self.save_data()
            return True
        return False

    def contact_healthcare_provider(self, provider_contact, patient_contact):
        print(f"Contacting healthcare provider: {provider_contact}")
        print(f"Patient contact information: {patient_contact}")
        print("Message sent to healthcare provider.")


def main():
    healthlink_system = HealthLinkSystem()

    while True:
        print("\nMain Menu:")
        print("1. View Health Education Resources")
        print("2. Emergency Services Information")
        print("3. Find Nearest Healthcare Facilities")
        print("4. COVID-19 Information and Updates")
        print("5. General Health Tips")
        print("6. Vaccination Information")
        print("7. Mental Health Resources")
        print("8. First Aid Guidelines")
        print("9. Contact Us")
        print("10. Exit")

        choice = input("Enter your choice (1-11): ")

        if choice == '1':
            login_signup_menu(healthlink_system)
        elif choice == '2':
            view_health_education_resources(healthlink_system)
        elif choice == '3':
            display_emergency_services_info()
        elif choice == '4':
            find_nearest_healthcare_facilities()
        elif choice == '5':
            display_covid19_info()
        elif choice == '6':
            display_general_health_tips()
        elif choice == '7':
            display_vaccination_info()
        elif choice == '8':
            display_mental_health_resources()
        elif choice == '9':
            display_first_aid_guidelines()
        elif choice == '10':
            display_contact_info()
        elif choice == '11':
            healthlink_system.save_staff_profiles()
            print("Exiting the HealthLink System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 11.")


def login_signup_menu(healthlink_system):
    while True:
        print("\nLogin/Signup Menu:")
        print("1. Hospital Staff Login")
        print("2. Patient Portal Login")
        print("3. Create Staff Profile")
        print("4. Create Patient Account")
        print("5. Return to Main Menu")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            hospital_staff_menu(healthlink_system)
        elif choice == '2':
            patient_portal_menu(healthlink_system)
        elif choice == '3':
            healthlink_system.create_staff_profile()
        elif choice == '4':
            create_patient_account(healthlink_system)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


def create_patient_account(healthlink_system):
    name = input("Enter patient name: ")
    password = input("Enter password: ")
    condition = input("Enter medical condition: ")
    medications = input("Enter medications (comma-separated): ").split(', ')
    allergies = input("Enter allergies (comma-separated): ").split(', ')
    access_code = healthlink_system.generate_access_code()
    
    new_patient = Patient(name, access_code, condition, medications, allergies, datetime.now())
    healthlink_system.add_patient(new_patient)
    
    print(f"Patient account created successfully. Your access code is: {access_code}")
    print("Please keep this access code safe, as you'll need it to log in.")


def hospital_staff_menu(healthlink_system):
    name = input("Enter your name: ")
    password = input("Enter your password: ")

    for provider in healthlink_system.providers:
        if provider.name == name and provider.password == password:
            while True:
                print("\nHospital Staff Menu:")
                print("1. Access Patient Medical Records")
                print("2. Register a New Patient")
                print("3. Update Patient Medical Information")
                print("4. Print Medical Records")
                print("5. List Access Codes")
                print("6. Check Appointment Reminders")
                print("7. Schedule Appointment")
                print("8. Reschedule Appointment")
                print("9. Cancel Appointment")
                print("10. Generate Patient Report")
                print("11. View Current Inventory")
                print("12. Update Inventory")
                print("13. View Bed Occupancy")
                print("14. Update Bed Availability")
                print("15. Add Medical Reminder for Patient")
                print("16. Update Medical Reminder for Patient")
                print("17. Request Medication Refill for Patient")
                print("18. Contact Healthcare Provider")
                print("19. View Health Education Resources")
                print("20. Logout")

                choice = input("Enter your choice (1-20): ")

                if choice.isdigit():
                    choice = int(choice)
                    if choice == 1:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            print_medical_records(patient)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 2:
                        name = input("Enter patient's name: ")
                        condition = input("Enter medical condition: ")
                        medications = input("Enter medications (comma-separated): ").split(', ')
                        allergies = input("Enter allergies (comma-separated): ").split(', ')
                        location = input("Enter patient's location (optional): ")
                        patient = Patient(name, healthlink_system.generate_access_code(), condition, medications, allergies, datetime.now())
                        provider.add_patient(patient)
                        print(f"Patient {name} registered with access code: {patient.access_code}")

                    elif choice == 3:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            update_patient_medical_info(patient)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 4:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            print_medical_records(patient)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 5:
                        provider.list_access_codes()

                    elif choice == 6:
                        patient_name = input("Enter patient's name: ")
                        if patient_name in healthlink_system.appointment_reminders:
                            print(f"Appointment Reminder: Your appointment is on {healthlink_system.appointment_reminders[patient_name]}.")
                        else:
                            print("No appointment scheduled for this patient.")

                    elif choice == 7:
                        access_code = input("Enter patient's access code: ")
                        appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            healthlink_system.schedule_appointment(patient, appointment_date)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 8:
                        access_code = input("Enter patient's access code: ")
                        new_appointment_date = input("Enter new appointment date (YYYY-MM-DD): ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            healthlink_system.reschedule_appointment(patient, new_appointment_date)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 9:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            healthlink_system.cancel_appointment(patient)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 10:
                        healthlink_system.generate_patient_report()

                    elif choice == 11:
                        healthlink_system.view_current_inventory()

                    elif choice == 12:
                        healthlink_system.update_inventory()

                    elif choice == 13:
                        healthlink_system.view_bed_occupancy()

                    elif choice == 14:
                        healthlink_system.update_bed_availability()

                    elif choice == 15:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            medication = input("Enter medication name: ")
                            frequency = input("Enter medication reminder frequency: ")
                            patient.add_medication_reminder(medication, frequency)
                            print("Medication reminder added successfully.")
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 16:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            if patient.medication_reminders:
                                print("Current Medication Reminders:")
                                for i, reminder in enumerate(patient.medication_reminders):
                                    print(f"{i+1}. Medication: {reminder['medication']}, Frequency: {reminder['frequency']}")
                                index = int(input("Enter the index of the reminder to update: "))
                                medication = input("Enter updated medication name: ")
                                frequency = input("Enter updated medication reminder frequency: ")
                                patient.medication_reminders[index - 1] = {'medication': medication, 'frequency': frequency}
                                print("Medication reminder updated successfully.")
                            else:
                                print("No medication reminders set.")
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 17:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            medication = input("Enter medication name: ")
                            quantity = int(input("Enter quantity: "))
                            healthlink_system.request_medication_refill(patient, medication, quantity)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 18:
                        access_code = input("Enter patient's access code: ")
                        patient = provider.access_medical_record(access_code)
                        if patient:
                            provider_contact = input("Enter provider's contact information: ")
                            patient_contact = input("Enter patient's contact information: ")
                            healthlink_system.contact_healthcare_provider(provider_contact, patient_contact)
                        else:
                            print("Access denied. Invalid access code.")

                    elif choice == 19:
                        healthlink_system.view_health_education_resources()

                    elif choice == 20:
                        print("Logging out...")
                        break
                    else:
                        print("Invalid choice. Please enter a number between 1 and 20.")
                else:
                    print("Invalid input. Please enter a number.")
            break
    else:
        print("Invalid credentials. Please try again.")


def print_medical_records(patient):
    if patient.medical_records:
        print(f"Medical Records for {patient.name}:")
        for record in patient.medical_records:
            print(f"Condition: {record.condition}")
            print(f"Medications: {', '.join(record.medications)}")
            print(f"Allergies: {', '.join(record.allergies)}")
            print(f"Timestamp: {record.timestamp}")
            print("------------------------")
    else:
        print("No medical records found for this patient.")


def update_patient_medical_info(patient):
    condition = input("Enter updated medical condition: ")
    medications = input("Enter updated medications (comma-separated): ").split(', ')
    allergies = input("Enter updated allergies (comma-separated): ").split(', ')
    timestamp = datetime.now()
    patient.add_medical_record_entry(MedicalRecordEntry(condition, medications, allergies, timestamp))
    print("Patient medical information updated successfully.")


def view_health_education_resources(healthlink_system):
    print("\nHealth Education Resources:")
    for condition, url in healthlink_system.education_resources.items():
        print(f"{condition}: {url}")
    
    while True:
        print("\nOptions:")
        print("1. Search for a specific condition")
        print("2. Return to main menu")
        
        choice = input("Enter your choice (1-2): ")
        
        if choice == '1':
            search_term = input("Enter the condition you're looking for: ").lower()
            found = False
            for condition, url in healthlink_system.education_resources.items():
                if search_term in condition.lower():
                    print(f"{condition}: {url}")
                    found = True
            if not found:
                print("No matching conditions found.")
        elif choice == '2':
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


def patient_portal_menu(healthlink_system):
    while True:
        print("\nPatient Portal Menu:")
        print("1. View Medical Records")
        print("2. Add Medication Reminder")
        print("3. Request Medication Refill")
        print("4. View Health Education Resources")
        print("5. Logout")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            access_code = input("Enter your access code: ")
            patient = healthlink_system.access_medical_record(access_code)
            if patient:
                print_medical_records(patient)
            else:
                print("Invalid access code.")

        elif choice == '2':
            access_code = input("Enter your access code: ")
            patient = healthlink_system.access_medical_record(access_code)
            if patient:
                medication = input("Enter the medication name: ")
                frequency = input("Enter the frequency of the reminder: ")
                patient.add_medication_reminder(medication, frequency)
                print("Medication reminder added successfully.")
            else:
                print("Invalid access code.")

        elif choice == '3':
            access_code = input("Enter your access code: ")
            patient = healthlink_system.access_medical_record(access_code)
            if patient:
                medication = input("Enter the medication name: ")
                quantity = input("Enter the quantity to refill: ")
                healthlink_system.request_medication_refill(patient, medication, quantity)
            else:
                print("Invalid access code.")

        elif choice == '4':
            healthlink_system.view_health_education_resources()

        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


def list_hospital_staff(staff_profiles):
    if staff_profiles:
        print("List of Hospital Staff:")
        for profile in staff_profiles:
            print(f"Name: {profile['name']}")
    else:
        print("No hospital staff profiles found.")


def display_emergency_services_info():
    print("\nEmergency Services Information:")
    print("- For immediate medical emergencies, dial 911")
    print("- Poison Control Center: 1-800-222-1222")
    print("- Local Emergency Room: [Your Hospital Name], [Address], [Phone Number]")
    print("- 24/7 Nurse Hotline: [Phone Number]")
    input("Press Enter to return to the main menu.")

def find_nearest_healthcare_facilities():
    print("\nFind Nearest Healthcare Facilities:")
    print("To find the nearest healthcare facilities, please visit:")
    print("https://www.healthcarefacilityfinder.com")
    print("Enter your location to see a list of nearby hospitals, clinics, and pharmacies.")
    input("Press Enter to return to the main menu.")

def display_covid19_info():
    print("\nCOVID-19 Information and Updates:")
    print("For the latest information on COVID-19, please visit:")
    print("- CDC: https://www.cdc.gov/coronavirus/2019-ncov/index.html")
    print("- WHO: https://www.who.int/emergencies/diseases/novel-coronavirus-2019")
    print("- Local Health Department: [Your Local Health Department Website]")
    input("Press Enter to return to the main menu.")

def display_general_health_tips():
    print("\nGeneral Health Tips:")
    print("1. Stay hydrated by drinking at least 8 glasses of water daily.")
    print("2. Eat a balanced diet rich in fruits, vegetables, and whole grains.")
    print("3. Exercise regularly, aiming for at least 150 minutes of moderate activity per week.")
    print("4. Get 7-9 hours of sleep each night.")
    print("5. Practice good hygiene, including regular handwashing.")
    print("6. Manage stress through relaxation techniques or hobbies.")
    print("7. Avoid smoking and limit alcohol consumption.")
    print("8. Schedule regular check-ups with your healthcare provider.")
    input("Press Enter to return to the main menu.")

def display_vaccination_info():
    print("\nVaccination Information:")
    print("For comprehensive vaccination information, please visit:")
    print("- CDC Vaccines and Immunizations: https://www.cdc.gov/vaccines/index.html")
    print("- WHO Immunization: https://www.who.int/health-topics/vaccines-and-immunization")
    print("Contact your healthcare provider or local health department for personalized vaccination recommendations.")
    input("Press Enter to return to the main menu.")

def display_mental_health_resources():
    print("\nMental Health Resources:")
    print("- National Suicide Prevention Lifeline: 1-800-273-TALK (8255)")
    print("- Crisis Text Line: Text HOME to 741741")
    print("- SAMHSA's National Helpline: 1-800-662-HELP (4357)")
    print("- National Alliance on Mental Illness (NAMI): https://www.nami.org")
    print("- Mental Health America: https://www.mhanational.org")
    input("Press Enter to return to the main menu.")

def display_first_aid_guidelines():
    print("\nFirst Aid Guidelines:")
    print("For comprehensive first aid information, visit:")
    print("- Red Cross First Aid: https://www.redcross.org/take-a-class/first-aid")
    print("- Mayo Clinic First Aid Guide: https://www.mayoclinic.org/first-aid")
    print("Remember, in case of serious injuries or life-threatening situations, always call emergency services immediately.")
    input("Press Enter to return to the main menu.")

def display_contact_info():
    print("\nContact Us:")
    print("For general inquiries:")
    print("- Phone: [Your Health System's Phone Number]")
    print("- Email: info@healthlinksystem.com")
    print("- Address: [Your Health System's Address]")
    print("\nFor technical support:")
    print("- Phone: [Technical Support Phone Number]")
    print("- Email: support@healthlinksystem.com")
    input("Press Enter to return to the main menu.")

if __name__ == "__main__":
    main()

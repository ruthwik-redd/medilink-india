import os
import sys
from PIL import Image, ImageTk
import tkinter as tk

class MedicalRecordEntry:
    def __init__(self, condition, medications, allergies, timestamp, url=None):
        self.condition = condition
        self.medications = medications
        self.allergies = allergies
        self.timestamp = timestamp
        self.url = url

class Patient:
    def __init__(self, name, access_code, condition, medications, allergies, timestamp):
        self.name = name
        self.access_code = access_code
        self.medical_records = [MedicalRecordEntry(condition, medications, allergies, timestamp)]

    def add_medical_record_entry(self, record_entry):
        self.medical_records.append(record_entry)

class HealthcareProvider:
    def __init__(self, name):
        self.name = name
        self.patients = []

    def access_medical_record(self, patient, access_code):
        if access_code == patient.access_code:
            return patient.medical_records
        else:
            return "Access denied. Invalid access code."

    def add_patient(self, patient):
        self.patients.append(patient)

class HealthLinkSystem:
    def __init__(self):
        self.providers = []

    def register_provider(self, name):
        provider = HealthcareProvider(name)
        self.providers.append(provider)
        return provider

    def register_patient(self, name, access_code, condition, medications, allergies, timestamp, provider):
        patient = Patient(name, access_code, condition, medications, allergies, timestamp)
        provider.add_patient(patient)
        return patient

    def add_medical_record_entry(self, patient):
        condition = input("Enter updated medical condition: ")
        medications = input("Enter medications (comma-separated): ").split(', ')
        allergies = input("Enter allergies (comma-separated): ").split(', ')
        timestamp = input("Enter the timestamp (optional): ")
        url = input("Enter URL (optional): ")

        record_entry = MedicalRecordEntry(condition, medications, allergies, timestamp, url)
        patient.add_medical_record_entry(record_entry)
        print("Medical record has been updated successfully.")

    def update_medical_record(self, patient):
        if not patient.medical_records:
            print("No medical records found for this patient.")
            return

        print("Current Medical Records:")
        for i, record in enumerate(patient.medical_records):
            print(f"{i + 1}. Condition: {record.condition}, Timestamp: {record.timestamp}")

        record_index = int(input("Enter the index of the record to update (0 to cancel): "))
        if record_index == 0:
            return

        if record_index < 1 or record_index > len(patient.medical_records):
            print("Invalid index. Please enter a valid index.")
            return

        record_index -= 1  # Adjust to match the list index

        condition = input("Enter updated medical condition: ")
        medications = input("Enter updated medications (comma-separated): ").split(', ')
        allergies = input("Enter updated allergies (comma-separated): ").split(', ')
        timestamp = input("Enter the timestamp (optional): ")
        url = input("Enter URL (optional): ")

        patient.medical_records[record_index] = MedicalRecordEntry(condition, medications, allergies, timestamp, url)
        print("Medical record has been updated successfully.")

    def print_medical_records(self, patient):
        print(f"Medical Records for Patient: {patient.name}")
        for record in patient.medical_records:
            print(f"Condition: {record.condition}")
            print(f"Medications: {', '.join(record.medications)}")
            print(f"Allergies: {', '.join(record.allergies)}")
            print(f"Timestamp: {record.timestamp}")
            if record.url:
                print(f"URL: {record.url}")
            print("------------------------")

    def share_medical_record(self, access_code, provider):
        for p in self.providers:
            for patient in p.patients:
                if access_code == patient.access_code:
                    return patient if provider in self.providers else None
        return None

def resource_path0(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Load the background image
bg_image_path = resource_path0("pexels-miguel-á-padriñán-255379.jpg")
bg_image = Image.open(bg_image_path)

healthlink_system = HealthLinkSystem()

# Create Tkinter window
window = tk.Tk()
window.title("HealthLink System")

# Set window size to the size of the background image
window.geometry(f"{bg_image.width}x{bg_image.height}")

# Convert the image for Tkinter
tk_image = ImageTk.PhotoImage(bg_image)

# Create a label with the background image
background_label = tk.Label(window, image=tk_image)
background_label.place(relwidth=1, relheight=1)

provider1 = healthlink_system.register_provider("City Hospital")
provider2 = healthlink_system.register_provider("General Clinic")

# Main menu for hospitals and patients
while True:
    print("\nMain Menu:")
    print("1. Hospital")
    print("2. Patient")
    print("3. Exit")
    main_choice = input("Enter your choice (1/2/3): ")

    if main_choice == '1':
        current_provider = None
        while True:
            print("\nHospital Menu:")
            print("1. Switch to City Hospital")
            print("2. Switch to General Clinic")
            print("3. Back to Main Menu")
            hospital_choice = input("Enter your choice (1/2/3): ")

            if hospital_choice == '1':
                current_provider = provider1
            elif hospital_choice == '2':
                current_provider = provider2
            elif hospital_choice == '3':
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

            if current_provider:
                print(f"\nOptions for {current_provider.name}:")
                print("1. Access Medical Records")
                print("2. Register a New Patient")
                print("3. Update Patient Medical Information")
                print("4. Print Medical Records")
                print("5. Back to Hospital Menu")
                provider_choice = input("Enter your choice (1/2/3/4/5): ")

                if provider_choice == '1':
                    access_code = input("Enter access code: ")
                    patient = healthlink_system.share_medical_record(access_code, current_provider)
                    if patient:
                        healthlink_system.print_medical_records(patient)
                    else:
                        print("Access denied. Invalid access code.")

                elif provider_choice == '2':
                    name = input("Enter patient's name: ")
                    access_code = input("Set access code for the patient: ")
                    condition = input("Enter medical condition: ")
                    medications = input("Enter medications (comma-separated): ").split(', ')
                    allergies = input("Enter allergies (comma-separated): ").split(', ')
                    timestamp = input("Enter the timestamp (optional): ")
                    healthlink_system.register_patient(name, access_code, condition, medications, allergies, timestamp, current_provider)

                elif provider_choice == '3':
                    access_code = input("Enter access code: ")
                    patient = healthlink_system.share_medical_record(access_code, current_provider)
                    if patient:
                        healthlink_system.update_medical_record(patient)
                    else:
                        print("Access denied. Invalid access code.")

                elif provider_choice == '4':
                    access_code = input("Enter access code: ")
                    patient = healthlink_system.share_medical_record(access_code, current_provider)
                    if patient:
                        healthlink_system.print_medical_records(patient)
                    else:
                        print("Access denied. Invalid access code.")

                elif provider_choice == '5':
                    current_provider = None

                else:
                    print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

    elif main_choice == '2':
        access_code = input("Enter your access code: ")
        patient = healthlink_system.share_medical_record(access_code, None)
        if patient:
            healthlink_system.print_medical_records(patient)
        else:
            print("Access denied. Invalid access code.")

    elif main_choice == '3':
        break

    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

window.mainloop()

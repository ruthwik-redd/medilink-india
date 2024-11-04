let healthlinkSystem = {
    providers: [],
    patients: [],
    currentProvider: null,

    init() {
        // Load stored data from localStorage
        const storedData = localStorage.getItem('healthlinkData');
        if (storedData) {
            const data = JSON.parse(storedData);
            this.providers = data.providers || [];
            this.patients = data.patients || [];
        }

        // Load the current provider from localStorage
        const storedProvider = localStorage.getItem('currentProvider');
        if (storedProvider) {
            this.currentProvider = JSON.parse(storedProvider);
        }
    },

    saveData() {
        // Save providers and patients to localStorage
        const data = {
            providers: this.providers,
            patients: this.patients
        };
        localStorage.setItem('healthlinkData', JSON.stringify(data));
    },

    registerProvider(name, username, password) {
        const provider = { name, username, password, patients: [] };
        this.providers.push(provider);
        this.saveData(); // Save data after registering a provider
        return provider;
    },

    registerPatient(name, accessCode, condition, medications, allergies, timestamp) {
        if (!this.currentProvider) {
            alert("You must be logged in to register a patient.");
            return;
        }

        const patient = {
            name: name || "Anonymous Patient",
            accessCode: accessCode,
            medicalRecords: [{ condition, medications, allergies, timestamp }]
        };
        this.currentProvider.patients.push(patient);
        this.patients.push(patient);
        this.saveData(); // Save data after registering a patient
        alert('Patient registered successfully!');
        window.location.href = 'index.html';
    },

    accessMedicalRecord(accessCode) {
        return this.patients.find(patient => patient.accessCode === accessCode);
    },

    searchPatient(searchTerm) {
        return this.patients.filter(patient => 
            patient.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
            patient.accessCode === searchTerm
        );
    },

    authenticateProvider(username, password) {
        const provider = this.providers.find(provider => 
            provider.username === username && provider.password === password
        );
        if (provider) {
            this.currentProvider = provider;
            localStorage.setItem('currentProvider', JSON.stringify(provider)); // Save current provider
            return provider;
        }
        return null;
    },

    logout() {
        this.currentProvider = null;
        localStorage.removeItem('currentProvider'); // Remove current provider from localStorage
    },

    keepUserLoggedIn() {
        const storedProvider = localStorage.getItem('currentProvider');
        if (storedProvider) {
            this.currentProvider = JSON.parse(storedProvider);
        }
    }
};

// Initialize the system
healthlinkSystem.init();
healthlinkSystem.keepUserLoggedIn();

// Event listeners for forms
document.getElementById('registerPatientForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const accessCode = document.getElementById('access_code').value;
    const condition = document.getElementById('condition').value;
    const medications = document.getElementById('medications').value.split(', ');
    const allergies = document.getElementById('allergies').value.split(', ');
    const timestamp = new Date().toISOString();

    healthlinkSystem.registerPatient(name, accessCode, condition, medications, allergies, timestamp);
});

document.getElementById('viewRecordsForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const accessCode = document.getElementById('access_code').value;
    const patient = healthlinkSystem.accessMedicalRecord(accessCode);
    const recordsContainer = document.getElementById('recordsContainer');

    if (patient) {
        recordsContainer.innerHTML = `<h2>Medical Records for ${patient.name}</h2>`;
        patient.medicalRecords.forEach(record => {
            recordsContainer.innerHTML += `
                <h3>Condition: ${record.condition}</h3>
                <p>Medications: ${record.medications.join(', ')}</p>
                <p>Allergies: ${record.allergies.join(', ')}</p>
                <p>Timestamp: ${record.timestamp}</p>
                <hr>
            `;
        });
    } else {
        recordsContainer.innerHTML = '<p>No records found for this access code.</p>';
    }
});

document.getElementById('searchPatientForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const searchTerm = document.getElementById('search_term').value;
    const results = healthlinkSystem.searchPatient(searchTerm);
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = '';

    if (results.length > 0) {
        results.forEach(patient => {
            searchResults.innerHTML += `<p>Patient Name: ${patient.name}, Access Code: ${patient.accessCode}</p>`;
        });
    } else {
        searchResults.innerHTML = '<p>No patients found.</p>';
    }
});

document.getElementById('loginForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const provider = healthlinkSystem.authenticateProvider(username, password);

    if (provider) {
        window.location.href = 'dashboard.html';
    } else {
        alert('Invalid username or password.');
    }
});

// Function to handle signup
document.getElementById('signupForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const providerName = document.getElementById('providerName').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    healthlinkSystem.registerProvider(providerName, username, password);
    alert('Signup successful! You can now log in.');
    window.location.href = 'login.html';
});

// Add logout functionality
document.getElementById('logoutButton')?.addEventListener('click', function() {
    healthlinkSystem.logout();
    alert('You have been logged out.');
    window.location.href = 'index.html';
});

// Populate provider name in dashboard
if (document.getElementById('providerName')) {
    document.getElementById('providerName').innerText = `Welcome, ${healthlinkSystem.currentProvider?.name || 'Guest'}`;
}

// Function to display medical records based on access code
function displayMedicalRecords() {
    const urlParams = new URLSearchParams(window.location.search);
    const accessCode = urlParams.get('access_code');
    const patient = healthlinkSystem.accessMedicalRecord(accessCode);
    const recordsContainer = document.getElementById('recordsContainer');

    if (patient) {
        recordsContainer.innerHTML = `<h2>Medical Records for ${patient.name}</h2>`;
        patient.medicalRecords.forEach(record => {
            recordsContainer.innerHTML += `
                <h3>Condition: ${record.condition}</h3>
                <p>Medications: ${record.medications.join(', ')}</p>
                <p>Allergies: ${record.allergies.join(', ')}</p>
                <p>Timestamp: ${record.timestamp}</p>
                <hr>
            `;
        });
    } else {
        recordsContainer.innerHTML = '<p>No records found for this access code.</p>';
    }
}

// Call the function to display medical records when the page loads
window.onload = displayMedicalRecords;

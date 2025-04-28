document.addEventListener('DOMContentLoaded', function() {
    const dobInput = document.getElementById('id_date_of_birth');
    const ageDisplay = document.createElement('span');
    ageDisplay.style.marginLeft = '10px';
    ageDisplay.style.fontWeight = 'bold';

    if (dobInput) {
        dobInput.parentNode.appendChild(ageDisplay);

        function calculateAge(dob) {
            const today = new Date();
            const birthDate = new Date(dob);
            let age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            return age;
        }

        function updateAge() {
            const dobValue = dobInput.value;
            if (dobValue) {
                const age = calculateAge(dobValue);
                if (!isNaN(age) && age >= 0) {
                    ageDisplay.textContent = 'Age: ' + age;
                } else {
                    ageDisplay.textContent = '';
                }
            } else {
                ageDisplay.textContent = '';
            }
        }

        dobInput.addEventListener('change', updateAge);
        updateAge();  // Initial call in case value is pre-filled
    }
});

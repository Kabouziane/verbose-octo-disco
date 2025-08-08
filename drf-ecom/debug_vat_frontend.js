// Test de validation TVA depuis le navigateur
async function testVATValidation() {
    const vatNumber = 'BE0874355129';
    
    console.log('Test validation TVA:', vatNumber);
    
    try {
        const response = await fetch('http://localhost:8000/api/shop/validate-vat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ vat_number: vatNumber })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.valid) {
            console.log('✅ TVA valide');
            console.log('Entreprise:', data.company_name);
            console.log('Adresse:', data.company_address);
        } else {
            console.log('❌ TVA invalide');
            console.log('Erreur:', data.error);
        }
        
    } catch (error) {
        console.error('❌ Erreur réseau:', error);
    }
}

// Exécuter le test
testVATValidation();
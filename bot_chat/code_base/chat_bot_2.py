import numpy as np
import pyttsx3
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

# Training data - mở rộng dataset để model học tốt hơn
X_train = np.array([
    [1, 1, 0, 1, 0, 0],  # Flu
    [0, 1, 1, 0, 0, 0],  # Cold
    [1, 1, 0, 0, 1, 0],  # COVID-19
    [0, 0, 1, 0, 0, 1],  # Allergy
    [1, 0, 0, 1, 0, 0],  # Flu variant 2
    [0, 1, 1, 1, 0, 0],  # Cold variant 2
    [1, 1, 1, 0, 1, 0],  # COVID-19 variant 2
    [0, 0, 1, 0, 0, 1],  # Allergy variant 2
    [1, 1, 0, 1, 1, 0],  # Flu + COVID symptoms
    [0, 1, 1, 1, 0, 1],  # Cold + Allergy symptoms
], dtype=np.float32)

y_train = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1])  # Labels
diseases = ["Flu", "Cold", "COVID-19", "Allergy"]


def build_and_train_model():
    """Build and train a neural network model using scikit-learn."""
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    # Create and train model
    model = MLPClassifier(
        hidden_layer_sizes=(16, 16),
        activation='relu',
        solver='adam',
        max_iter=2000,
        random_state=42,
        learning_rate_init=0.01,
        alpha=0.01,  # L2 regularization
        early_stopping=True,
        validation_fraction=0.1
    )

    model.fit(X_scaled, y_train)
    return model, scaler


# Build and train the model
print("🤖 Initializing AI model...")
model, scaler = build_and_train_model()
print("✅ Model trained successfully!")


def speak(text):
    """Convert text to speech using pyttsx3."""
    try:
        engine = pyttsx3.init()
        # Thiết lập tốc độ nói chậm hơn
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 50)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️ Speech synthesis not available: {e}")


def predict_with_uncertainty(model, scaler, x, n_iter=50):
    """
    Predict with uncertainty estimation using multiple predictions.
    Simulates Monte Carlo dropout by adding small noise.
    """
    x_scaled = scaler.transform(x)

    # Get base prediction
    base_probs = model.predict_proba(x_scaled)

    # Simulate uncertainty by adding small random noise and re-predicting
    predictions = []
    for _ in range(n_iter):
        # Add small noise to simulate uncertainty
        noise = np.random.normal(0, 0.05, x_scaled.shape)
        x_noisy = x_scaled + noise

        # Clip to valid range
        x_noisy = np.clip(x_noisy, -2, 2)

        try:
            pred = model.predict_proba(x_noisy)
            predictions.append(pred)
        except:
            predictions.append(base_probs)

    # Calculate mean and std
    predictions = np.array(predictions)
    mean = predictions.mean(axis=0)
    std = predictions.std(axis=0)

    return mean, std


def get_confidence_level(std_val):
    """Convert standard deviation to confidence level description."""
    if std_val < 0.1:
        return "Very High"
    elif std_val < 0.2:
        return "High"
    elif std_val < 0.3:
        return "Medium"
    else:
        return "Low"


def run_virtual_robot():
    """Main function to run the virtual health assistant."""
    print("\n" + "=" * 60)
    print("🤖 VIRTUAL HEALTH ASSISTANT ROBOT")
    print("=" * 60)
    print("Hello! I am your AI health assistant.")
    print("I will analyze your symptoms and provide a preliminary diagnosis.")
    print("⚠️  Note: This is for educational purposes only!")
    print("Always consult a real doctor for medical advice.")
    print("-" * 60)

    symptom_names = [
        "Fever", "Cough", "Sneezing",
        "Fatigue", "Loss of Taste", "Itchy Eyes"
    ]

    # Collect symptoms from user
    print("\nPlease answer the following questions with Y/N:")
    input_symptoms = []

    for i, name in enumerate(symptom_names, 1):
        while True:
            ans = input(f"{i}. Do you have {name}? (Y/N): ").strip().lower()
            if ans in ['y', 'yes', 'n', 'no']:
                input_symptoms.append(1 if ans in ['y', 'yes'] else 0)
                break
            else:
                print("   Please enter Y (Yes) or N (No)")

    # Make prediction with uncertainty
    input_array = np.array([input_symptoms], dtype=np.float32)
    mean_probs, std_probs = predict_with_uncertainty(model, scaler, input_array)

    # Get most likely diagnosis
    most_likely = np.argmax(mean_probs)
    diagnosis = diseases[most_likely]
    confidence = mean_probs[0][most_likely]
    uncertainty = std_probs[0][most_likely]

    # Display results
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS")
    print("=" * 60)

    print(f"\n🏥 Primary Diagnosis: {diagnosis}")
    print(f"🎯 Confidence: {confidence:.1%}")
    print(f"📈 Certainty Level: {get_confidence_level(uncertainty)}")

    print(f"\n📋 Detailed Probabilities:")
    for i, disease in enumerate(diseases):
        prob = mean_probs[0][i]
        unc = std_probs[0][i]
        bar = "█" * int(prob * 20)  # Visual bar
        print(f"   {disease:12}: {prob:.1%} ±{unc:.3f} {bar}")

    # Speak the diagnosis
    speak_text = f"Based on your symptoms, you may have {diagnosis} with {confidence:.0%} confidence."
    speak(speak_text)

    # Recommendation maps
    test_map = {
        "Flu": "Influenza A/B rapid test",
        "Cold": "Nasal swab for viral culture",
        "COVID-19": "RT-PCR test or rapid antigen test",
        "Allergy": "Allergy skin prick test or IgE blood test"
    }

    medicine_map = {
        "Flu": "Oseltamivir (Tamiflu), rest, and fluids",
        "Cold": "Rest, fluids, throat lozenges, and antihistamines",
        "COVID-19": "Isolation, rest, Paracetamol, and monitor symptoms",
        "Allergy": "Antihistamines (Loratadine/Cetirizine), avoid allergens"
    }

    prevention_map = {
        "Flu": "Annual flu vaccination, frequent hand washing",
        "Cold": "Hand hygiene, avoid close contact with sick people",
        "COVID-19": "Vaccination, mask wearing, social distancing",
        "Allergy": "Identify and avoid triggers, keep environment clean"
    }

    # Provide recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 30)
    print(f"🔬 Recommended Test: {test_map[diagnosis]}")
    print(f"💊 Treatment Options: {medicine_map[diagnosis]}")
    print(f"🛡️  Prevention: {prevention_map[diagnosis]}")

    # Speak recommendations
    speak(f"I recommend you take a {test_map[diagnosis]} and consider {medicine_map[diagnosis]}")

    # Create visualization
    plt.figure(figsize=(12, 8))

    # Main bar chart
    plt.subplot(2, 1, 1)
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    bars = plt.bar(
        diseases,
        mean_probs[0],
        yerr=std_probs[0],
        capsize=8,
        color=colors,
        alpha=0.8,
        edgecolor='navy',
        linewidth=1.5
    )

    # Add percentage labels on bars
    for bar, prob in zip(bars, mean_probs[0]):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                 f'{prob:.1%}', ha='center', va='bottom', fontweight='bold')

    plt.ylabel("Probability", fontsize=12, fontweight='bold')
    plt.title("🏥 AI Diagnosis Results with Uncertainty Estimation",
              fontsize=14, fontweight='bold', pad=20)
    plt.ylim(0, 1.1)
    plt.grid(axis='y', alpha=0.3)

    # Symptoms visualization
    plt.subplot(2, 1, 2)
    symptom_colors = ['red' if s else 'lightgray' for s in input_symptoms]
    plt.bar(range(len(symptom_names)), input_symptoms,
            color=symptom_colors, alpha=0.7)
    plt.xticks(range(len(symptom_names)), symptom_names, rotation=45, ha='right')
    plt.ylabel("Present (1) / Absent (0)")
    plt.title("📝 Your Reported Symptoms", fontweight='bold')
    plt.ylim(-0.1, 1.1)

    plt.tight_layout()
    plt.show()

    # Final disclaimer
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT MEDICAL DISCLAIMER")
    print("=" * 60)
    print("This AI assistant provides preliminary analysis only.")
    print("It is NOT a substitute for professional medical advice.")
    print("Please consult a qualified healthcare provider for:")
    print("• Accurate diagnosis")
    print("• Proper treatment")
    print("• Medical emergencies")
    print("=" * 60)


# Run the virtual health assistant
if __name__ == "__main__":
    run_virtual_robot()
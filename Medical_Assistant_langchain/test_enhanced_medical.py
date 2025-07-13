#!/usr/bin/env python3
"""
Test script for enhanced medical assistant with medication recommendations
"""
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.langchain_service import MedicalChatService
from config import Config

def test_medication_recommendations():
    """Test the enhanced medication recommendation capabilities"""
    
    print("🏥 Testing Enhanced Medical Assistant with Medication Recommendations")
    print("=" * 70)
    
    try:
        # Initialize the service
        chat_service = MedicalChatService()
        session_id = "test_session"
        
        # Test cases
        test_cases = [
            {
                "query": "I have a severe headache and fever of 101°F",
                "expected": "specific medications with dosages"
            },
            {
                "query": "I'm experiencing chest pain and shortness of breath",
                "expected": "emergency protocol and medications"
            },
            {
                "query": "I need information about ibuprofen dosage for back pain",
                "expected": "detailed medication information"
            },
            {
                "query": "I have type 2 diabetes and need medication recommendations",
                "expected": "comprehensive diabetes medication plan"
            }
        ]
        
        print("\n🧪 Running Test Cases:\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case['query']}")
            print("-" * 50)
            
            try:
                response = chat_service.chat(test_case['query'], session_id)
                print(f"Response: {response[:200]}...")
                print(f"Expected: {test_case['expected']}")
                print("✅ Test completed successfully\n")
                
            except Exception as e:
                print(f"❌ Test failed: {e}\n")
        
        print("🎯 Testing Specialized Methods:\n")
        
        # Test medication prescription method
        print("Testing medication prescription method...")
        try:
            prescription = chat_service.get_medication_prescription(
                condition="hypertension",
                patient_age=45,
                allergies="none",
                current_meds="none"
            )
            print(f"Prescription Response: {prescription[:200]}...")
            print("✅ Prescription method test completed\n")
        except Exception as e:
            print(f"❌ Prescription method test failed: {e}\n")
        
        # Test comprehensive consultation
        print("Testing comprehensive consultation method...")
        try:
            consultation = chat_service.get_comprehensive_medical_consultation(
                symptoms="persistent cough and fatigue",
                age=35,
                medical_history="no significant history"
            )
            print(f"Consultation Response: {consultation[:200]}...")
            print("✅ Consultation method test completed\n")
        except Exception as e:
            print(f"❌ Consultation method test failed: {e}\n")
        
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("Please check your configuration and ensure the Supabase table is created.")

if __name__ == "__main__":
    test_medication_recommendations()

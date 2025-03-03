from django.shortcuts import render
from .services import generate_question, get_answer 
 # Ensure your import is correct

def home(request):
    if request.method == "POST":
        text = request.POST.get('text', '').strip()  # Get and clean input text
        num_questions = request.POST.get('numQuestions', '5')  # Get numQuestions from form
        try:
            num_questions = int(num_questions)  # Convert to integer
        except ValueError:
            num_questions = 5  # Default to 5 if conversion fails

        if text:  # Check if text is not empty
            questions = generate_question(text, num_questions)  # Pass both arguments
            return render(request, 'base.html', {'questions': questions})  
        else:
            error_message = "Please enter some text to generate questions."
            return render(request, 'base.html', {'error_message': error_message})  
    else:
        return render(request, 'base.html')  # Render the form on GET request
def exam(request):
    return render(request,'exam.html')
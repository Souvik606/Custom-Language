import subprocess
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Temporarily disable CSRF for testing (enable properly in production)
def run_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            # Save code to a temporary file
            with open("temp_code.txt", "w") as temp_file:
                temp_file.write(code)
            
            # Run the code using your custom interpreter
            result = subprocess.run(
                ["python", "path_to_your_interpreter.py", "temp_code.txt"],
                capture_output=True, text=True, timeout=5
            )
            return JsonResponse({
                "stdout": result.stdout,
                "stderr": result.stderr
            })
        except subprocess.TimeoutExpired:
            return JsonResponse({"error": "Execution timed out."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def index(request):
    return render(request, 'editor/base.html')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

def chat_widget(request):
    return render(request, 'chatbot/chat_widget.html')

@csrf_exempt
@require_POST
def send_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()
        
        # Simple response logic
        responses = {
            'hello': 'Hi there! How can I help you today?',
            'hi': 'Hello! How can I assist you?',
            'how are you': "I'm just a bot, but I'm here to help!",
            'products': 'We have a wide range of products. You can browse our categories to find what you\'re looking for!',
            'contact': 'You can contact our support team at support@example.com',
            'shipping': 'We offer free shipping on orders over $50. Standard delivery takes 3-5 business days.',
            'return': 'You can return items within 30 days of delivery. Please visit our Returns page for more details.',
            'bye': 'Goodbye! Feel free to come back if you have more questions!',
            'help': 'I can help with: products, shipping, returns, and more. Just ask!',
            'price': 'Prices vary by product. Please check the product page for specific pricing.',
            'thank': 'You\'re welcome! Is there anything else I can help you with?'
        }
        
        # Check for keywords in the message
        response = "I'm not sure how to help with that. Could you try asking something else?"
        for key in responses:
            if key in user_message:
                response = responses[key]
                break
        
        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

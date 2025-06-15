from flask import Flask, request, jsonify

app = Flask(__name__)

def process_card(ccx):
    ccx = ccx.strip()
    try:
        n, mm, yy, cvc = ccx.split("|")
    except ValueError:
        return {
            "cc": ccx,
            "response": "Invalid card format. Use: NUMBER|MM|YY|CVV",
            "status": "Invalid"
        }

    if "20" in yy:
        yy = yy.split("20")[1]

    return {
        "cc": f"{n}|{mm}|{yy}|{cvc}",
        "response": "tere behan ki bacterial chut mai hathi ka lauda dal k 100inc ka gadha banadunga",
        "status": "Declined"
    }

@app.route('/gate=stripe5/key=wasdark/cc=<path:cc>', methods=['GET'])
def check_card(cc):
    result = process_card(cc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5698)

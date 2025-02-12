import json
import urllib.request
import epics
import time

def get_pv(pv):

    test = epics.caget(pv)
    if test == 1:
        print ("Beam is active, not necessary to create beam")
        return False
    elif test == 0:
        return True
    else:
        return False

def post_request(api_url, payload, headers=None):
    """
    Envoie une requête POST à l'API spécifiée.

    Args:
        api_url (str): L'URL de l'API.
        payload (dict): Les données à envoyer dans le corps de la requête.
        headers (dict, optional): Les en-têtes de la requête. Par défaut None.

    Returns:
        dict: La réponse JSON de l'API si disponible, sinon texte brut.
    """
    # Convertir le payload en chaîne JSON
    data = json.dumps(payload).encode("utf-8")

    # Créer une requête
    request = urllib.request.Request(api_url, data=data, method="PUT")

    # Ajouter les en-têtes
    if headers:
        for key, value in headers.items():
            request.add_header(key, value)
    else:
        # Par défaut, spécifiez que nous envoyons du JSON
        request.add_header("content-type", "application/json")

    try:
        # Envoyer la requête et lire la réponse
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode("utf-8")
            # Tenter de décoder la réponse en JSON
            try:
                return json.loads(response_data)
            except json.JSONDecodeError:
                return {"error": "La réponse n'est pas au format JSON", "content": response_data}
    except urllib.error.URLError as e:
        return {"error": "Une erreur est survenue lors de la requête", "details": str(e)}


if __name__ == "__main__":
    # Exemple d'utilisation
    api_url = "http://10.0.197.19:8080/Olog/logs"
    pv = "SL-APP-MCS:BOM-CPU:StartBeamCmd"

    payload =  {
                   "owner": "admin",
                   "description": f"Manual shutbeam due to {pv}",
                   "level": "Info",
                   "title": "Log created from python script",
                   "logbooks": [
                       {
                           "name": "tests"
                       }
                   ]
               }

    headers = {
    ### To do: s'authentifier via login/password
        "Authorization": "Basic $TOKEN",
        "content-type": "application/json"
    }


    # Variable de contrôle
    execute_flag = False

    # Boucle d'attente
    print("En attente que la variable 'execute_flag' soit True...")
    while not execute_flag:
        time.sleep(1)
        execute_flag = get_pv(pv)

    # Appeler la fonctio
    response = post_request(api_url, payload, headers)
    if response:
        # Afficher le résultat
        print("Réponse de l'API :", response)

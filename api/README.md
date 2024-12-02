Exercice API - TechLab - Python
ANDRIANARIVELO Ranto Billy

# Fontionnalités :

## Inscription / Login / Logout / Password Reset
Après inscription, un email est envoyé à l'adresse email de l'utilisateur en lui
indiquant d'activer son compte avant de se connecter, sinon impossible d'effectuer un login
Chaque utilisateur peut se déconnecter à tout moment
Si un utilisateur veut réinitialiser son mot de passe, il doit entrer un adresse email existant
puis il reçoit un email de réinitialisation de mot de passe avec un "token" unique,
puis il va être redirigé vers un lien pour qu'il puisse saisir son nouveau mot de passe,
après l'API va vérifier si l'utilisateur a bien saisi son adresse email et a utilisé un token valide pour
valider la réinitialisation

## Gestion d'annonces
- Un utilisateur peut créer plusieurs annonces et peut y ajouter des images
- Un utilisateur peut modifier le titre d'une annonce, peut supprimer les images existants dans cette annonce
- Un utilisateur ne peut pas commenter sa propre annonce
- Un utilisateur peut consulter les annonces des autres utilisateurs y compris les détails
- Un utilisateur peut commenter une annonce d'un autre utilisateur
- Un utilisateur peut supprimer/modifier son commentaire sur une annonce mais ne peut pas faire ces actions sur
les commentaires des autres utilisateur


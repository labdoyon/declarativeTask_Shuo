
supported_languages = ['french', 'english']

picturesNamesEnglish = {
    'a001': 'penguin',
    'a002': 'pig',
    'a003': 'snake',
    'a004': 'squirrel',
    'a005': 'turtle',
    'a006': 'crocodile',
    'a007': 'bear',
    'a008': 'deer',
    'a009': 'dog',
    'a010': 'eagle',
    'a011': 'elephant',
    'a012': 'fish',
    'a013': 'rabbit',
    'a014': 'rhinoceros',
    'a015': 'sheep',
    'a016': 'rooster',
    'a017': 'bird',
    'a018': 'cat',
    'a019': 'duck',
    'a020': 'racoon',

    'b001': 'pliers',
    'b002': 'power outlet',
    'b003': 'fridge',
    'b004': 'chair',
    'b005': 'rolling pin',
    'b006': 'salt',
    'b007': 'television',
    'b008': 'watering can',
    'b009': 'glass',
    'b010': 'hammer',
    'b011': 'key',
    'b012': 'lamp',
    'b013': 'saw',
    'b014': 'pan',
    'b015': 'screwdriver',
    'b016': 'spoon',
    'b017': 'axe',
    'b018': 'broom',
    'b019': 'table',
    'b020': 'toaster',
    
    'c001': 'pants',
    'c002': 'shoe',
    'c003': 'skirt',
    'c004': 'sock',
    'c005': 'pullover',
    'c006': 'tie',
    'c007': 'jacket',
    'c008': 'belt',
    'c009': 'dress',
    'c010': 'hat',
    'c011': 'coat',
    'c012': 'mitten',
    'c013': 'necklace',
    'c014': 'glove',
    'c015': 'button',
    'c016': 'purse',
    'c017': 'ribbon',
    'c018': 'watch',
    'c019': 'shirt',
    'c020': 'cap'
}

picturesNamesFrench = {
    'a001': 'pingouin',
    'a002': 'cochon',
    'a003': 'serpent',
    'a004': 'écureuil',
    'a005': 'tortue',
    'a006': 'crocodile',
    'a007': 'ours',
    'a008': 'cerf',
    'a009': 'chien',
    'a010': 'aigle',
    'a011': 'éléphant',
    'a012': 'poisson',
    'a013': 'lapin',
    'a014': 'rhinocéros',
    'a015': 'mouton',
    'a016': 'coq',
    'a017': 'oiseau',
    'a018': 'chat',
    'a019': 'canard',
    'a020': 'raton laveur',

    'b001': 'pinces',
    'b002': 'prise',
    'b003': 'réfrigérateur',
    'b004': 'chaise',
    'b005': 'rouleau',
    'b006': 'sel',
    'b007': 'télévision',
    'b008': 'arrosoir',
    'b009': 'verre',
    'b010': 'marteau',
    'b011': 'clé',
    'b012': 'lampe',
    'b013': 'scie',
    'b014': 'casserole',
    'b015': 'tournevis',
    'b016': 'cuillère',
    'b017': 'hache',
    'b018': 'balai',
    'b019': 'table',
    'b020': 'grille-pain',

    'c001': 'pantalon',
    'c002': 'chaussure',
    'c003': 'jupe',
    'c004': 'chaussette',  # bas?
    'c005': 'pull',
    'c006': 'cravate',
    'c007': 'veste',
    'c008': 'ceinture',
    'c009': 'robe',
    'c010': 'chapeau',
    'c011': 'manteau',
    'c012': 'moufle',
    'c013': 'collier',
    'c014': 'gant',
    'c015': 'bouton',
    'c016': 'sac à main',
    'c017': 'ruban',
    'c018': 'montre',
    'c019': 'chemise',
    'c020': 'casquette'
}

pictureNames = {'english': picturesNamesEnglish, 'french': picturesNamesFrench}
classNames = {'english': {'a': 'animals', 'b': 'household', 'c': 'clothes'},
              'french': {'a': 'animaux', 'b': 'maison', 'c': 'vêtements'},
              None: {'a': 'a', 'b': 'b', 'c': 'c'}}
soundNames = {
    None: {0: 'S1', 1: 'S2', 2: 'S3'},
    'english': {0: 'standard', 1: 'noise', 2: 'A'},
    'french': {0: 'standard', 1: 'bruit', 2: 'A'}}

sound_textbox = {'english': ' Sound: ', 'french': ' Son: '}
rest_screen_text = {'english': ' REST ', 'french': ' REPOS '}
ending_screen_text = {'english': ' THANK YOU ', 'french': ' MERCI '}
presentation_screen_text = {'english': ' PRESENTATION ', 'french': ' PRÉSENTATION '}
ttl_instructions_text = {'english': ' PLEASE INPUT TTL ', 'french': ' EN ATTENTE DU TTL '}
choose_image_text = {'english': ' Choose an image ', 'french': ' Choisissez une image '}
choose_position_text = {'english': ' Choose a location ', 'french': ' Choisissez une position '}
next_sound_text = {'english': ' Next Sound ', 'french': ' Suivant '}
ld_GUI_end_text = {'english': ' End ', 'french': ' Fin '}

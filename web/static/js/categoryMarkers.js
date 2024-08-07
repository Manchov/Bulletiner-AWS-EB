var categoryMarkers = {
    "Drug-related Crime": L.ExtraMarkers.icon({icon: 'fa-pills', markerColor: 'red', shape: 'square', prefix: 'fa'}),
    "Traffic Incident": L.ExtraMarkers.icon({icon: 'fa-car', markerColor: 'orange', shape: 'circle', prefix: 'fa'}),
    "Animal Incident": L.ExtraMarkers.icon({icon: 'fa-paw', markerColor: 'green', shape: 'star', prefix: 'fa'}),
    "Corruption": L.ExtraMarkers.icon({icon: 'fa-balance-scale', markerColor: 'blue', shape: 'square', prefix: 'fa'}),
    "Workplace Incident": L.ExtraMarkers.icon({
        icon: 'fa-briefcase',
        markerColor: 'yellow',
        shape: 'circle',
        prefix: 'fa'
    }),
    "Aggressive Behavior": L.ExtraMarkers.icon({icon: 'fa-angry', markerColor: 'purple', shape: 'star', prefix: 'fa'}),
    "Weather-related Accident": L.ExtraMarkers.icon({
        icon: 'fa-cloud-showers-heavy',
        markerColor: 'cyan',
        shape: 'square',
        prefix: 'fa'
    }),
    "Attempted Murder": L.ExtraMarkers.icon({
        icon: 'fa-skull-crossbones',
        markerColor: 'black',
        shape: 'circle',
        prefix: 'fa'
    }),
    "Robbery/Burglary": L.ExtraMarkers.icon({icon: 'fa-mask', markerColor: 'violet', shape: 'square', prefix: 'fa'}),
    "Sexual Offense": L.ExtraMarkers.icon({icon: 'fa-genderless', markerColor: 'pink', shape: 'star', prefix: 'fa'}),
    "Assault": L.ExtraMarkers.icon({icon: 'fa-hand-rock', markerColor: 'red', shape: 'circle', prefix: 'fa'}),
    "Theft": L.ExtraMarkers.icon({icon: 'fa-hand-paper', markerColor: 'green', shape: 'square', prefix: 'fa'}),
    "Vandalism": L.ExtraMarkers.icon({icon: 'fa-spray-can', markerColor: 'blue', shape: 'circle', prefix: 'fa'}),
    "Domestic Violence": L.ExtraMarkers.icon({icon: 'fa-home', markerColor: 'orange', shape: 'square', prefix: 'fa'}),
    "Fraud/Embezzlement": L.ExtraMarkers.icon({
        icon: 'fa-money-bill-wave',
        markerColor: 'yellow',
        shape: 'star',
        prefix: 'fa'
    }),
    "Cybercrime": L.ExtraMarkers.icon({icon: 'fa-laptop', markerColor: 'cyan', shape: 'circle', prefix: 'fa'}),
    "Kidnapping/Abduction": L.ExtraMarkers.icon({
        icon: 'fa-child',
        markerColor: 'purple',
        shape: 'square',
        prefix: 'fa'
    }),
    "Missing Person": L.ExtraMarkers.icon({icon: 'fa-user-slash', markerColor: 'pink', shape: 'star', prefix: 'fa'}),
    "Homicide": L.ExtraMarkers.icon({icon: 'fa-cross', markerColor: 'black', shape: 'circle', prefix: 'fa'}),
    "Arson": L.ExtraMarkers.icon({icon: 'fa-fire', markerColor: 'red', shape: 'square', prefix: 'fa'}),
    "Public Intoxication/Disorderly Conduct": L.ExtraMarkers.icon({
        icon: 'fa-beer',
        markerColor: 'green',
        shape: 'circle',
        prefix: 'fa'
    }),
    "Illegal Possession of Firearms": L.ExtraMarkers.icon({
        icon: 'fa-gun',
        markerColor: 'blue',
        shape: 'square',
        prefix: 'fa'
    }),
    "Trespassing": L.ExtraMarkers.icon({icon: 'fa-door-open', markerColor: 'orange', shape: 'circle', prefix: 'fa'}),
    "Child Abuse": L.ExtraMarkers.icon({icon: 'fa-child', markerColor: 'purple', shape: 'square', prefix: 'fa'}),
    "Human Trafficking": L.ExtraMarkers.icon({
        icon: 'fa-hand-holding-heart',
        markerColor: 'pink',
        shape: 'star',
        prefix: 'fa'
    }),
    "Identity Theft": L.ExtraMarkers.icon({icon: 'fa-id-card', markerColor: 'black', shape: 'circle', prefix: 'fa'}),
    "Terrorism": L.ExtraMarkers.icon({icon: 'fa-bomb', markerColor: 'red', shape: 'square', prefix: 'fa'}),
    "Gang-related Activity": L.ExtraMarkers.icon({
        icon: 'fa-users',
        markerColor: 'green',
        shape: 'circle',
        prefix: 'fa'
    }),
    "Public Nuisance": L.ExtraMarkers.icon({icon: 'fa-bullhorn', markerColor: 'blue', shape: 'square', prefix: 'fa'}),
    "Riot/Unlawful Assembly": L.ExtraMarkers.icon({
        icon: 'fa-flag',
        markerColor: 'orange',
        shape: 'circle',
        prefix: 'fa'
    }),
    "Environmental Crime": L.ExtraMarkers.icon({icon: 'fa-leaf', markerColor: 'purple', shape: 'star', prefix: 'fa'}),
    "Hate Crime": L.ExtraMarkers.icon({icon: 'fa-heart-broken', markerColor: 'pink', shape: 'circle', prefix: 'fa'}),
    "Prostitution": L.ExtraMarkers.icon({icon: 'fa-venus-mars', markerColor: 'black', shape: 'square', prefix: 'fa'}),
    "Extortion/Bribery": L.ExtraMarkers.icon({icon: 'fa-handshake', markerColor: 'red', shape: 'circle', prefix: 'fa'}),
    "Forgery/Counterfeiting": L.ExtraMarkers.icon({
        icon: 'fa-file-invoice-dollar',
        markerColor: 'green',
        shape: 'square',
        prefix: 'fa'
    }),
    "Smuggling": L.ExtraMarkers.icon({icon: 'fa-shipping-fast', markerColor: 'blue', shape: 'circle', prefix: 'fa'}),
    "Escape from Custody": L.ExtraMarkers.icon({
        icon: 'fa-running',
        markerColor: 'orange',
        shape: 'square',
        prefix: 'fa'
    }),
    "Violation of Court Order/Probation": L.ExtraMarkers.icon({
        icon: 'fa-gavel',
        markerColor: 'purple',
        shape: 'star',
        prefix: 'fa'
    }),
    "Suspicious Activity": L.ExtraMarkers.icon({
        icon: 'fa-user-secret',
        markerColor: 'pink',
        shape: 'circle',
        prefix: 'fa'
    }),
    "Attempted Suicide": L.ExtraMarkers.icon({
        icon: 'fa-heartbeat',
        markerColor: 'black',
        shape: 'square',
        prefix: 'fa'
    }),
    "Stalking/Harassment": L.ExtraMarkers.icon({icon: 'fa-eye', markerColor: 'red', shape: 'circle', prefix: 'fa'}),
    "Illegal Dumping": L.ExtraMarkers.icon({icon: 'fa-trash', markerColor: 'green', shape: 'square', prefix: 'fa'}),
    "Illegal Gambling": L.ExtraMarkers.icon({icon: 'fa-dice', markerColor: 'blue', shape: 'circle', prefix: 'fa'}),
    "Noise Complaint": L.ExtraMarkers.icon({
        icon: 'fa-volume-up',
        markerColor: 'orange',
        shape: 'square',
        prefix: 'fa'
    }),
    "Underage Drinking": L.ExtraMarkers.icon({
        icon: 'fa-wine-bottle',
        markerColor: 'purple',
        shape: 'star',
        prefix: 'fa'
    }),
    "Loitering": L.ExtraMarkers.icon({icon: 'fa-clock', markerColor: 'pink', shape: 'circle', prefix: 'fa'}),
    "Unlawful Possession of Controlled Substances": L.ExtraMarkers.icon({
        icon: 'fa-syringe',
        markerColor: 'black',
        shape: 'square',
        prefix: 'fa'
    }),
    "Reckless Endangerment": L.ExtraMarkers.icon({
        icon: 'fa-exclamation-triangle',
        markerColor: 'red',
        shape: 'circle',
        prefix: 'fa'
    }),
    "Vehicle Theft": L.ExtraMarkers.icon({icon: 'fa-car-side', markerColor: 'green', shape: 'square', prefix: 'fa'}),
    "Obstruction of Justice": L.ExtraMarkers.icon({
        icon: 'fa-gavel',
        markerColor: 'blue',
        shape: 'circle',
        prefix: 'fa'
    })
};

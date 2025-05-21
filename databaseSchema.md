## Structure de la base de données MongoDB


### Collection `mangas`

Cette collection stocke les informations générales sur les mangas :

```json
{
  "_id": "ObjectId(...)",
  "title": "Nom du manga",
  "alt_title": "Nom alternatif",
  "url": "https://anime-sama.fr/catalogue/...",
  "image_url": "https://anime-sama.fr/assets/images/...",
  "genres": ["Action", "Drama", "..."],
  "type": "Scans",
  "language": "VOSTFR",
  "scan_types": [
    {
      "name": "Scan VF",
      "url": "https://anime-sama.fr/catalogue/...",
      "chapters_count": 42
    }
  ],
  "updated_at": "2025-05-20T14:30:00.000Z"
}
```

### Collection `chapters`

Cette collection stocke les informations détaillées sur chaque chapitre, avec une référence au manga parent :

```json
{
  "_id": "ObjectId(...)",
  "manga_title": "Nom du manga",
  "scan_name": "Scan VF",
  "number": "1",
  "title": "Chapitre 1",
  "reader_path": "reader.php?path=...",
  "added_at": "2025-05-20T14:30:00.000Z"
}
```

Ou pour les chapitres avec des URLs d'images :

```json
{
  "_id": "ObjectId(...)",
  "manga_title": "Nom du manga",
  "scan_name": "Scan VF",
  "number": "2",
  "title": "Chapitre 2",
  "image_urls": ["https://...", "https://..."],
  "page_count": 24,
  "added_at": "2025-05-20T14:30:00.000Z"
}
```

### Indexation

La base de données utilise plusieurs index pour optimiser les performances :

1. Index unique sur le champ `title` dans la collection `mangas`
2. Index composé unique sur les champs `manga_title`, `scan_name` et `number` dans la collection `chapters`

### Accéder aux données

Exemples de requêtes MongoDB pour accéder aux données :

```javascript
// Rechercher un manga par titre
db.mangas.findOne({ title: "Nom du manga" })

// Obtenir tous les chapitres d'un manga spécifique
db.chapters.find({ manga_title: "Nom du manga" }).sort({ number: 1 })

// Obtenir les chapitres d'un type de scan spécifique
db.chapters.find({ manga_title: "Nom du manga", scan_name: "Scan VF" })

// Trouver un chapitre spécifique
db.chapters.findOne({ 
  manga_title: "Nom du manga", 
  scan_name: "Scan VF", 
  number: "1" 
})
```

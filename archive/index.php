<?php
// Load card data
$json = file_get_contents(__DIR__ . '/data/cards.json');
$cards = json_decode($json, true);

// Group cards by category, preserving sort order
$categories = [];
foreach ($cards as $card) {
    $categories[$card['category']][] = $card;
}

// Category display order
$categoryOrder = ['Auditory', 'Cognitive', 'Intersectional', 'Mental Health', 'Neurodiversity', 'Physical', 'Speech', 'Visual'];
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Inclusive Design Persona Cards</title>
  <meta name="description" content="A collection of 40 inclusive design persona cards representing diverse users with disabilities, cognitive differences, situational impairments, and more. Use these personas to build more accessible digital products.">
  <link rel="stylesheet" href="css/style.css">
	<link href="https://fonts.googleapis.com" rel="stylesheet">
</head>
<body>

  <a class="skip-link" href="#main-content">Skip to main content</a>

  <header class="site-header" role="banner">
    <div class="header-inner">
      <h1>Inclusive Design Persona Cards</h1>
      <p class="tagline">40 personas. Every kind of user. Better products for everyone.</p>
    </div>
  </header>

  <main id="main-content">

    <section class="page-intro" aria-labelledby="intro-heading">
      <h2 id="intro-heading" class="visually-hidden">About These Cards</h2>
      <p>
        Great products are built for everyone&mdash;not just the majority. These persona cards represent
        real experiences of people with disabilities, chronic conditions, situational impairments, and
        cognitive differences. By designing with these personas in mind from the start, your team can
        uncover barriers early, build empathy across disciplines, and ship products that work for the
        full spectrum of human diversity. Use them in design critiques, sprint planning, accessibility
        audits, and AI development to keep diverse users at the center of every decision.
      </p>
    </section>

    <?php foreach ($categoryOrder as $categoryName): ?>
      <?php if (!isset($categories[$categoryName])) continue; ?>
      <section class="category-section" aria-labelledby="cat-<?= htmlspecialchars(strtolower(str_replace(' ', '-', $categoryName))) ?>">
        <h2 id="cat-<?= htmlspecialchars(strtolower(str_replace(' ', '-', $categoryName))) ?>">
          <?= htmlspecialchars($categoryName) ?>
        </h2>

        <ul class="cards-grid" role="list">
          <?php foreach ($categories[$categoryName] as $card): ?>
            <?php
              $cardSlug = strtolower(preg_replace('/[^a-z0-9]+/i', '-', $card['title']));
              $cardUrl  = 'card.php?id=' . $card['id'];
            ?>
            <li>
              <article class="card-preview" aria-labelledby="card-title-<?= $card['id'] ?>">
                <header class="card-preview__header">
                  <p>
                    <?= htmlspecialchars($categoryName) ?>
                  </p>
                  <h3 id="card-title-<?= $card['id'] ?>"><?= htmlspecialchars($card['title']) ?></h3>
                  <p class="card-preview__name"><?= htmlspecialchars($card['name']) ?></p>
                </header>

                <div class="card-preview__body">
                  <p class="card-preview__backstory"><?= htmlspecialchars($card['backstory']) ?></p>
                </div>

                <footer class="card-preview__footer">
                  <a class="card-link" href="<?= htmlspecialchars($cardUrl) ?>">
                    View <?= htmlspecialchars($card['title']) ?> card
                    <span class="visually-hidden">for <?= htmlspecialchars($card['name']) ?></span>
                  </a>
                </footer>
              </article>
            </li>
          <?php endforeach; ?>
        </ul>
      </section>
    <?php endforeach; ?>

  </main>

  <footer class="site-footer" role="contentinfo">
    <p>Inclusive Design Persona Cards &mdash; Helping teams build accessible, human-centered products.</p>
  </footer>

</body>
</html>

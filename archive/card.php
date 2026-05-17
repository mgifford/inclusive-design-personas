<?php
// Load all cards
$json  = file_get_contents(__DIR__ . '/data/cards.json');
$cards = json_decode($json, true);

// Validate ID parameter
$requestedId = isset($_GET['id']) ? (int) $_GET['id'] : 0;

// Find the requested card
$card = null;
foreach ($cards as $c) {
    if ($c['id'] === $requestedId) {
        $card = $c;
        break;
    }
}

// 404 if card not found
if ($card === null) {
    http_response_code(404);
    include __DIR__ . '/404.php';
    exit;
}

// Find related cards (same category, excluding current)
$relatedCards = array_filter($cards, fn($c) => $c['category'] === $card['category'] && $c['id'] !== $card['id']);

// Page title
$pageTitle = htmlspecialchars($card['title']) . ' — Inclusive Design Persona Cards';

// Assistive technologies already an array from JSON
$assistiveTechs = $card['assistiveTechnologies'];
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><?= $pageTitle ?></title>
  <meta name="description" content="Inclusive design persona card for <?= htmlspecialchars($card['title']) ?> (<?= htmlspecialchars($card['category']) ?>). Learn about digital challenges, assistive technologies, and design considerations.">
  <link rel="stylesheet" href="css/style.css">
	<link href="https://fonts.googleapis.com" rel="stylesheet">
</head>
<body>

  <a class="skip-link" href="#main-content">Skip to main content</a>

  <header class="site-header" role="banner">
    <div class="header-inner">
      <h1><a href="index.php">Inclusive Design Persona Cards</a></h1>
    </div>
  </header>

  <main id="main-content">

    <!-- Breadcrumb navigation -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
        <li><a href="index.php">All Cards</a></li>
        <li>
          <a href="index.php#cat-<?= htmlspecialchars(strtolower(str_replace(' ', '-', $card['category']))) ?>">
            <?= htmlspecialchars($card['category']) ?>
          </a>
        </li>
        <li><span aria-current="page"><?= htmlspecialchars($card['title']) ?></span></li>
      </ol>
    </nav>

    <!-- Print button (screen only) -->
    <button class="print-btn no-print" onclick="window.print()" type="button">
      <svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="6 9 6 2 18 2 18 9"></polyline>
        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
        <rect x="6" y="14" width="12" height="8"></rect>
      </svg>
      Print this card
    </button>

    <!-- ══════════════════════════════════════════════════════
         SCREEN VIEW: Full card detail
         ══════════════════════════════════════════════════════ -->
    <article class="card-detail no-print" aria-labelledby="card-heading">

      <header class="card-detail__header">
        <span class="card-detail__category"><?= htmlspecialchars($card['category']) ?></span>
        <h2 id="card-heading"><?= htmlspecialchars($card['title']) ?></h2>
        <p class="card-detail__persona-name">Persona: <?= htmlspecialchars($card['name']) ?></p>
        <p class="card-detail__backstory"><?= htmlspecialchars($card['backstory']) ?></p>
      </header>

      <section class="card-section" aria-labelledby="section-condition">
        <h3 id="section-condition">About This Condition</h3>
        <p><?= htmlspecialchars($card['conditionDescription']) ?></p>
      </section>

      <section class="card-section" aria-labelledby="section-challenges">
        <h3 id="section-challenges">Digital Challenges</h3>
        <p><?= htmlspecialchars($card['digitalChallenges']) ?></p>
      </section>

      <section class="card-section" aria-labelledby="section-assistive">
        <h3 id="section-assistive">Assistive Technologies</h3>
        <ul class="assistive-tech-list"><?php foreach ($assistiveTechs as $tech): ?><li><?= htmlspecialchars(trim($tech)) ?></li><?php endforeach; ?></ul>
      </section>

      <section class="card-section" aria-labelledby="section-design">
        <h3 id="section-design">Design Considerations</h3>
        <p><?= htmlspecialchars($card['designConsiderations']) ?></p>
      </section>

      <?php if (!empty($card['clinicalExamples'])): ?>
      <section class="card-section" aria-labelledby="section-clinical">
        <h3 id="section-clinical">Clinical Examples</h3>
        <p class="clinical-examples"><?= htmlspecialchars($card['clinicalExamples']) ?></p>
      </section>
      <?php endif; ?>

      <!-- Related cards — shown within the card article -->
      <?php if (!empty($relatedCards)): ?>
      <section class="card-section related-cards-section" aria-labelledby="related-heading">
        <h3 id="related-heading">Related <?= htmlspecialchars($card['category']) ?> Cards</h3>
        <ul class="related-cards-list" role="list">
          <?php foreach ($relatedCards as $related): ?>
            <li>
              <a href="card.php?id=<?= $related['id'] ?>">
                <?= htmlspecialchars($related['title']) ?>
                <span class="visually-hidden">— <?= htmlspecialchars($related['name']) ?></span>
              </a>
            </li>
          <?php endforeach; ?>
        </ul>
      </section>
      <?php endif; ?>

    </article>

    <!-- AI Prompt section (screen only) -->
    <?php if (!empty($card['aiPromptUrl'])): ?>
    <aside class="ai-prompt-section no-print" aria-labelledby="ai-prompt-heading">
      <h3 id="ai-prompt-heading">AI Development Prompt</h3>
      <p>Incorporate <?= htmlspecialchars($card['title']) ?> into your AI development with this prompt.</p>
      <?php if (!empty($card['aiPrompt'])): ?>
      <div class="ai-prompt-wrapper">
        <div class="ai-prompt-toolbar">
          <span class="ai-prompt-label">Prompt</span>
          <button class="copy-prompt-btn" type="button"
                  onclick="copyPrompt(this)"
                  aria-label="Copy AI prompt text to clipboard">
            <svg aria-hidden="true" focusable="false" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            Copy prompt
          </button>
        </div>
        <pre class="ai-prompt-code"><code><?= htmlspecialchars($card['aiPrompt']) ?></code></pre>
      </div>
      <?php endif; ?>
      <a class="ai-prompt-link"
         href="<?= htmlspecialchars($card['aiPromptUrl']) ?>"
         target="_blank"
         rel="noopener noreferrer"
         aria-label="Open AI prompt for <?= htmlspecialchars($card['title']) ?> (opens in new tab)">
        Use the <?= htmlspecialchars($card['title']) ?> AI Prompt ↗
      </a>
    </aside>
    <?php endif; ?>


    <!-- ══════════════════════════════════════════════════════
         PRINT VIEW: Foldable card layout
         Front (left) + Back (right)
         Both fit in the top half of a portrait letter page.
         Fold the right panel behind the left to create a
         double-sided card.
         ══════════════════════════════════════════════════════ -->
    <div class="print-only" role="presentation">

      <div class="print-card-wrapper">

        <!-- FRONT of card -->
        <div class="print-card-front">
          <span class="print-category"><?= htmlspecialchars($card['category']) ?></span>
          <h1><?= htmlspecialchars($card['title']) ?></h1>
          <p class="print-name"><?= htmlspecialchars($card['name']) ?></p>
          <p class="print-backstory"><?= htmlspecialchars($card['backstory']) ?></p>
          <p class="print-condition"><?= htmlspecialchars($card['conditionDescription']) ?></p>
          <?php if (!empty($relatedCards)): ?>
          <div class="print-related">
            <strong>Related:</strong>
            <?= htmlspecialchars(implode(', ', array_map(fn($r) => $r['title'], $relatedCards))) ?>
          </div>
          <?php endif; ?>
        </div>

        <!-- BACK of card -->
        <div class="print-card-back">

          <h3>Digital Challenges</h3>
          <p><?= htmlspecialchars($card['digitalChallenges']) ?></p>

          <h3>Assistive Technologies</h3>
          <ul>
            <?php foreach ($assistiveTechs as $tech): ?>
              <li><?= htmlspecialchars(trim($tech)) ?></li>
            <?php endforeach; ?>
          </ul>

          <h3>Design Considerations</h3>
          <p><?= htmlspecialchars($card['designConsiderations']) ?></p>

          <?php if (!empty($card['aiPromptUrl'])): ?>
          <h3>AI Development Prompt</h3>
          <p>Incorporate <?= htmlspecialchars($card['title']) ?> into your AI development with this prompt:</p>
          <p class="print-ai-url"><?= htmlspecialchars($card['aiPromptUrl']) ?></p>
          <?php endif; ?>

        </div>

      </div>

      <p class="print-fold-guide">✂ Fold right panel behind left panel to create a double-sided card</p>

    </div>

  </main>

  <footer class="site-footer no-print" role="contentinfo">
    <p>
      <a href="index.php">← Back to all persona cards</a>
      &nbsp;&mdash;&nbsp;
      Inclusive Design Persona Cards
    </p>
  </footer>

  <script>
  function copyPrompt(btn) {
    var code = btn.closest('.ai-prompt-wrapper').querySelector('code');
    var original = btn.innerHTML;
    navigator.clipboard.writeText(code.textContent).then(function () {
      btn.textContent = 'Copied!';
      btn.setAttribute('aria-label', 'Copied to clipboard');
      setTimeout(function () {
        btn.innerHTML = original;
        btn.setAttribute('aria-label', 'Copy AI prompt text to clipboard');
      }, 2000);
    }, function () {
      btn.textContent = 'Copy failed';
      setTimeout(function () { btn.innerHTML = original; }, 2000);
    });
  }
  </script>

</body>
</html>

# Batch receipt import plan

## Goal

Capture one or many receipts on an iPhone without a custom app. Once a week,
process the queued images on the Mac, extract transaction details with the
OpenAI API, review them, and create the approved transactions in YNAB.

## Workflow

1. In Photos, open the built-in Receipts collection (or search for receipts),
   select one or more images, and share them to a **Queue YNAB receipts**
   shortcut. The shortcut also accepts images shared from other apps.
2. The shortcut saves each image as a separate, uniquely named file in an
   iCloud Drive `YNAB Receipts/Inbox` folder. It makes no API calls and stores
   no API keys on the iPhone.
3. A command run on the Mac reads the synced inbox. It records an image hash
   before processing so rerunning the batch cannot silently submit the same
   image twice.
4. For each new image, the command calls an image-capable OpenAI model and
   requests structured data: merchant, purchase date, total, currency, and
   optional receipt number and tax. Preserve the original image and mark
   unreadable or ambiguous fields for review. Handle Swedish dates and decimal
   commas explicitly.
5. The command produces a review file with one proposed YNAB transaction per
   receipt. The user can correct the date, amount, account, payee, category,
   and memo, or skip a receipt. A photo with multiple purchases or unclear
   totals must not be posted automatically.
6. On a separate explicit submit command, validate each approved row, resolve
   the YNAB account and category IDs, check for likely duplicates already in
   YNAB, and create transactions through the YNAB API. Record the returned
   transaction IDs, then move successful images to `Archive`; leave failed or
   skipped images available for retry.

## Local design

- **iPhone:** Apple Shortcuts share-sheet action: receive images, repeat over
  each image, assign a unique filename, and save to the iCloud inbox without
  asking for a destination each time.
- **Mac:** Python command-line batch processor. A weekly manual run is enough;
  a scheduled run can be added later. The Mac needs to be on, iCloud Drive
  synced, and internet access available during processing.
- **Credentials:** Keep the existing `ynab_token.rtf` local. Supply an OpenAI
  API key through a local environment variable or ignored `.env` file. Do not
  put either key in the shortcut, repository, review file, or logs.
- **State:** Store a local processing journal outside Git with image hashes,
  extraction status, review status, YNAB transaction IDs, and errors. Write
  state atomically so an interrupted batch can resume safely.
- **Data sent out:** Receipt images go to the OpenAI API. Only approved
  transaction details go to YNAB. The photos and review files remain in the
  user's iCloud Drive and Mac storage.

## Build order

1. Create and test the iPhone shortcut with one image and a multi-image
   selection. Confirm filenames are unique and the Mac receives every image.
2. Build extraction and review-file generation with sample receipts. Test
   Swedish and non-Swedish formats, refunds, and unreadable photos.
3. Add account/category lookup and YNAB submission with a preview mode.
   Reuse the existing YNAB connection code where practical.
4. Add duplicate checks, restart-safe state, and archive/retry behavior.
5. Test an approved transaction end to end, then run a small weekly batch.

## Completion criteria

- Multiple photos can be queued in one share action.
- Repeating a batch does not create duplicate YNAB transactions.
- Every proposed transaction shows its source image and uncertain fields.
- Nothing is posted to YNAB until its review row is approved and the submit
  command is run.
- Successful submissions have a recorded YNAB transaction ID; failures remain
  retryable without losing the source receipt.

## Needed before implementation

- An OpenAI API key with billing enabled, stored locally on the Mac.
- The iCloud Drive folder path as it appears on the Mac.
- A few representative receipt images for extraction testing.
- A default YNAB account/category choice, or a rule for selecting them per
  receipt during review.

## References

- [Apple Shortcuts share sheet](https://support.apple.com/guide/shortcuts/apd163eb9f95/ios)
- [Apple Shortcuts file actions](https://support.apple.com/guide/shortcuts/apdaf74d75a5/ios)
- [OpenAI image inputs](https://developers.openai.com/api/docs/guides/images-vision)
- [OpenAI structured output](https://developers.openai.com/api/docs/guides/structured-outputs)
- [YNAB API endpoints](https://api.ynab.com/v1)

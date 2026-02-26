/**
 * Aruni Learning System - Daily Email Trigger
 *
 * This runs INSIDE the Google Sheet. No Python, no cron, no laptop needed.
 *
 * SETUP (one time, 2 minutes):
 *   1. Open the Aruni Google Sheet
 *   2. Extensions > Apps Script
 *   3. Delete any existing code, paste this entire file
 *   4. Click Save
 *   5. Click the clock icon (Triggers) on the left sidebar
 *   6. + Add Trigger:
 *        Function: sendDailyEmails
 *        Event source: Time-driven
 *        Type: Day timer
 *        Time: 7am to 8am
 *   7. Click Save, authorize when prompted
 *   8. Done! Emails will be sent every morning automatically.
 *
 * TEST: Click Run > sendDailyEmails to send a test email now.
 */

// SHEET ID - change this if you create a new sheet
var ARUNI_SHEET_ID = '1REuUPOdypTP2OBg-_o6SChN8byW_yX9c2vfGOxYnQQs';

function sendDailyEmails() {
  var ss = SpreadsheetApp.openById(ARUNI_SHEET_ID);
  var configSheet = ss.getSheetByName('config');

  if (!configSheet) {
    Logger.log('No config tab found');
    return;
  }

  var configData = configSheet.getDataRange().getValues();
  var today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  var todayDisplay = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'EEEE, MMMM d, yyyy');

  // Skip header row
  for (var i = 1; i < configData.length; i++) {
    var username = configData[i][0];
    var name = configData[i][1];
    var email = configData[i][2];
    var domain = configData[i][3];

    if (!username || !email) continue;

    try {
      var userSheet = ss.getSheetByName(username);
      if (!userSheet) {
        Logger.log('No tab found for user: ' + username);
        continue;
      }

      var data = userSheet.getDataRange().getValues();
      if (data.length <= 1) continue; // Only headers

      // Find concepts due for review (next_review <= today)
      var dueConcepts = [];
      for (var j = 1; j < data.length; j++) {
        var nextReview = data[j][6]; // Column G: next_review
        if (!nextReview) continue;

        var reviewDate;
        if (nextReview instanceof Date) {
          reviewDate = Utilities.formatDate(nextReview, Session.getScriptTimeZone(), 'yyyy-MM-dd');
        } else {
          reviewDate = nextReview.toString();
        }

        if (reviewDate <= today) {
          dueConcepts.push({
            topic: data[j][0],       // A: topic
            question: data[j][3],    // D: questions
            confidence: data[j][4] || 'Low',  // E: confidence
            timesReviewed: data[j][7] || 0     // H: times_reviewed
          });
        }
      }

      // Generate and send email
      var subject, body;
      if (dueConcepts.length === 0) {
        subject = 'All caught up! - ' + domain;
        body = buildNoDueEmail(name, domain, todayDisplay);
      } else {
        subject = dueConcepts.length + ' concept(s) to review - ' + domain;
        body = buildReviewEmail(name, domain, todayDisplay, dueConcepts);
      }

      MailApp.sendEmail({
        to: email,
        subject: subject,
        htmlBody: body,
        name: 'Aruni'
      });

      Logger.log('Sent to ' + email + ': ' + dueConcepts.length + ' concepts due');

    } catch (e) {
      Logger.log('Error for ' + username + ': ' + e.toString());
    }
  }
}


function buildReviewEmail(name, domain, todayDisplay, concepts) {
  var colors = { 'Low': '#e74c3c', 'Medium': '#f39c12', 'High': '#27ae60' };

  var questionsHtml = '';
  for (var i = 0; i < concepts.length; i++) {
    var c = concepts[i];
    var color = colors[c.confidence] || '#95a5a6';
    questionsHtml +=
      '<div style="background:#f8f9fa;padding:16px;border-radius:8px;margin:12px 0;border-left:4px solid ' + color + ';">' +
      '<strong>' + (i + 1) + '. ' + c.topic + '</strong>' +
      ' <span style="background:' + color + ';color:white;padding:2px 8px;border-radius:3px;font-size:12px;">' + c.confidence + '</span>' +
      '<br><br>' + (c.question || '(no question set)') +
      '<br><small style="color:#999;">Reviewed ' + c.timesReviewed + ' time(s)</small>' +
      '</div>';
  }

  return '<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;color:#333;">' +
    '<h2 style="color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:8px;">Your Daily Review</h2>' +
    '<p style="color:#666;">' + todayDisplay + '</p>' +
    '<p>Good morning ' + name + '! You have <strong>' + concepts.length + '</strong> concept(s) in <strong>' + domain + '</strong> ready for review.</p>' +
    '<h3>Answer from memory (no peeking!):</h3>' +
    questionsHtml +
    '<div style="background:#e3f2fd;padding:16px;border-radius:8px;margin:24px 0;text-align:center;">' +
    '<p style="margin:0;">Open your LLM and say: <strong>"I\'m ready to review"</strong></p>' +
    '</div>' +
    '<hr style="border:none;border-top:1px solid #eee;margin:24px 0;">' +
    '<p style="font-size:11px;color:#aaa;text-align:center;">Aruni Learning System</p>' +
    '</div>';
}


/**
 * Run this ONCE to set up the daily 7am trigger.
 * After running, you can verify under Triggers (clock icon) in the sidebar.
 */
function installDailyTrigger() {
  // Remove any existing triggers for this function to avoid duplicates
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'sendDailyEmails') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  // Create daily trigger at 7am
  ScriptApp.newTrigger('sendDailyEmails')
    .timeBased()
    .atHour(7)
    .everyDays(1)
    .create();
  Logger.log('Daily trigger installed for 7:00 AM');
}


function buildNoDueEmail(name, domain, todayDisplay) {
  return '<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;color:#333;">' +
    '<h2 style="color:#27ae60;">All caught up!</h2>' +
    '<p style="color:#666;">' + todayDisplay + '</p>' +
    '<p>' + name + ', no concepts due for review today in <strong>' + domain + '</strong>.</p>' +
    '<div style="background:#e8f5e9;padding:16px;border-radius:8px;margin:20px 0;">' +
    '<p><strong>Ideas for today:</strong></p>' +
    '<ul>' +
    '<li>Open your LLM and say <strong>"Teach me something new"</strong></li>' +
    '<li>Read something and discuss it with your LLM</li>' +
    '<li>Ask a question you have been curious about</li>' +
    '</ul>' +
    '</div>' +
    '<p style="font-size:11px;color:#aaa;text-align:center;">Aruni Learning System</p>' +
    '</div>';
}

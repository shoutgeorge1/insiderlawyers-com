# Form Setup – FormSubmit.co

The lead form uses **FormSubmit.co** to send submissions to `ial.leads.2024@gmail.com`.

## First-Time Activation (required)

FormSubmit requires email activation before it will deliver submissions.

1. **Submit a test lead** from your live form.
2. **Check `ial.leads.2024@gmail.com`** – FormSubmit sends an activation email.
3. **Check spam/junk** – activation emails often land there.
4. **Click the activation link** in that email to enable delivery.

Until this is done, submissions will not be delivered to your inbox.

## If Leads Still Don’t Arrive

- **Spam**: Check spam/junk and mark FormSubmit as “not spam.”
- **Activation string**: After activating, FormSubmit may give you a unique string. If delivery is unreliable, replace the email in the form action with that string (see FormSubmit docs).
- **Alternative services**: Consider Formspree, Getform, or Netlify Forms if FormSubmit is blocked by your provider.

## Form Configuration

- **Action**: `https://formsubmit.co/ial.leads.2024@gmail.com`
- **Reply-To**: Uses the lead’s email so you can reply directly.
- **Thank-you redirect**: Sends users to `/thank-you` after submission.

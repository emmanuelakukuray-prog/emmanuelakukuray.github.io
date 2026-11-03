const formStatus = document.querySelector("#form-status");
const submission = new URLSearchParams(window.location.search).get("submission");

const submissionMessages = {
  sent: {
    message: "Thanks for reaching out. Your message has been sent to our team.",
    isError: false,
  },
  error: {
    message: "We couldn't send your message right now. Please try again later or email info@rjtechnologies.com.",
    isError: true,
  },
  invalid: {
    message: "Please check the form details and try again.",
    isError: true,
  },
};

if (submission && formStatus && Object.hasOwn(submissionMessages, submission)) {
  const result = submissionMessages[submission];
  formStatus.textContent = result.message;
  formStatus.classList.toggle("is-error", result.isError);
  formStatus.hidden = false;
  formStatus.focus();
  window.history.replaceState({}, "", window.location.pathname);
} else if (!formStatus) {
  console.error("Contact form status could not be displayed: the status element is missing.");
}

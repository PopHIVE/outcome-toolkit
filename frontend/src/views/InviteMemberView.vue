<script setup lang="ts">
import { ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";
import { useProjectStore } from "@/stores/project";
import { computed } from "vue";

const router = useRouter();

const projectStore = useProjectStore();
const project = computed(() => projectStore.project());
const email = ref("");
const firstName = ref("");
const lastName = ref("");
const company = ref("");
const submitted = ref(false);
let errorSubmitting = ref(false);

// NOTE: These are restrictions from Okta.
// Both names are required, and cannot contain: =<+>;&quot;/\\|&";
// eslint-disable-next-line no-useless-escape -- We must double-escape the slashes to avoid having them interpolated during HTML processing.
const pattern = `[^<>+="&\\/\\\\]+`;
const invalidMessage = `Names cannot contain <+>&"=/\\`;

const formRef = useTemplateRef("invite-form-ref");
const formValid = ref(false);
watch([formRef, email, firstName, lastName, company], () => {
  formValid.value = !!formRef.value?.checkValidity();
});

const submit = () => {
  if (!project.value || !formValid.value) {
    return;
  }
  submitted.value = true;

  const newUser = {
    email: email.value,
    first_name: firstName.value,
    last_name: lastName.value,
    company: company.value,
    project_name: project.value.projectName,
    project_id: project.value.id,
  };

  fetch("/api/v2/send-email", {
    method: "POST",
    body: JSON.stringify({ newUser }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => {
      if (!res.ok) {
        throw res;
      }
      return res.json();
    })
    .catch((err) => {
      errorSubmitting.value = true;
      console.error("Error inviting team member", err); // TODO remove output of "err" before shipment
    });
};
</script>

<template>
  <main class="d-flex invite-member" id="invite">
    <div class="form">
      <h3>Invite New Team Member</h3>
      <template v-if="!submitted">
        <form ref="invite-form-ref">
          <label for="email" class="form-label">
            E-mail address for new team member to invite
          </label>
          <input
            class="form-control"
            v-model="email"
            type="email"
            id="email"
            placeholder="team_member@example.com"
            required />

          <label for="firstName" class="form-label">First Name</label>
          <input
            type="text"
            v-model="firstName"
            class="form-control"
            id="firstName"
            :pattern
            :placeholder="invalidMessage"
            required />

          <label for="lastName" class="form-label">Last Name</label>
          <input
            type="text"
            v-model="lastName"
            id="lastName"
            class="form-control"
            :pattern
            :placeholder="invalidMessage"
            required />

          <label for="company" class="form-label">Company</label>
          <input
            v-model="company"
            type="text"
            id="company"
            class="form-control"
            required
            placeholder="Company or organization name is required." />

          <label for="project">Project Name</label>
          <input
            :value="project?.projectName ?? ''"
            type="text"
            id="project"
            class="form-control"
            disabled />
          <p class="subtext">
            If your new team member does not have an account they will receive an e-mail invite from
            Okta (no-reply@okta.com) within 3-5 business days to set up their credentials.
          </p>
          <p v-if="!formValid" class="subtext text-center">* All fields are required</p>
          <button
            class="btn btn-primary mt-3 mx-auto d-block"
            :class="formValid ? 'btn-primary' : 'btn-outline-primary'"
            @click="submit"
            :disabled="!formValid"
            title="Submit new team member">
            Submit
          </button>
        </form>
      </template>
      <template v-else>
        <section class="confirmation-text">
          <p v-if="errorSubmitting" class="mt-4 mx-5 text-center">
            Error submitting team member. Please try again.
          </p>
          <p v-else class="mt-4 mx-5 text-center">
            Thank you for your submission. Your new team member will receive an e-mail invitation
            from Okta (no-reply@okta.com) within 3-5 business days to set up their credentials.
          </p>
          <p class="subtext">
            OKTA authentication services are provided for the Outcome Toolkit project.
          </p>
          <!-- TODO: Once Invite page has moved to the projects page, then route back to projects 
                    There is an auth issue with going to invite before projects and then getting redirected to login
                    Do not send user to projects unless they have first authenticated already          
          -->
          <!-- <button
            class="btn btn-invite mt-4 mx-auto d-block"
            title="Return to Project Dashboard"
            @click="router.push('/protected/projects')">
            Return to Project Dashboard
          </button> -->
          <button
            class="btn btn-primary mt-4 mx-auto d-block"
            title="Return to Home"
            @click="router.push('/')">
            Return to Home
          </button>
        </section>
      </template>
    </div>
  </main>
</template>

<style scoped>
.invite-member {
  align-items: center;
  background-color: var(--brand-cool-gray-10);
  box-sizing: border-box;
  gap: 2em;
  justify-content: center;
  justify-items: center;
  padding: 2em;
  height: calc(100vh - 7rem + 6px);
  min-width: 100%;
}

.form {
  background-color: var(--brand-white);
  max-width: 75%;
  padding: 2em;
  justify-content: center;
  align-items: center;
  display: flex;
  flex-direction: column;
  border-radius: 25px;
  input::placeholder {
    color: var(--brand-cool-gray-40);
  }
  input:invalid {
    background: #fee;
    &:placeholder-shown {
      outline-color: gray;
    }
  }
  label:has(+ input[required])::after {
    color: red;
    content: " *";
  }

  label {
    padding-top: 1em;
    font-weight: bold;
  }
}
.confirmation-text {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.subtext {
  font-style: italic;
  font-size: small;
  margin-top: 2em;
  margin-bottom: 0em;
}
h3 {
  font-weight: bold;
}
</style>

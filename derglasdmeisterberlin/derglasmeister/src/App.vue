<template>
  <main class="min-h-screen bg-gradient-to-br from-gray-100 via-white to-gray-200 p-6">
    <section class="max-w-5xl mx-auto grid md:grid-cols-3 gap-6 bg-white rounded-2xl shadow-xl overflow-hidden">
      
      <!-- Sidebar -->
      <aside class="bg-gray-800 text-white flex flex-col items-center gap-8 p-6 md:p-8">
        <div class="flex flex-col items-center w-full">
  <img
    src="/src/assets/karim.jpg"
    alt="Karim Bouziane"
    class="w-40 h-40 rounded-full border-4 border-white shadow-md mb-4 object-cover"
  />
  <h1 class="text-2xl font-bold text-center">Karim Bouziane</h1>
  <p class="text-lg text-gray-300 mb-2">Versatile Cook</p>
  <p class="text-sm text-gray-300 text-center mb-4">
    Berlin – Friedrichshain
  </p>

  <!-- Buttons moved up here -->
  <div class="space-y-3 w-full">
    <a
      :href="'tel:' + phone"
      class="block text-center w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-xl transition"
    >
      📞 Call Me
    </a>
    <a
      :href="'mailto:' + email"
      class="block text-center w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-xl transition"
    >
      ✉️ Send Email
    </a>
  </div>
</div>

      </aside>

      <!-- Main Content -->
      <div class="md:col-span-2 p-6 md:p-10 space-y-8">
        <!-- Profile -->
        <section>
          <h2 class="text-xl font-semibold text-gray-700 mb-2">Profile</h2>
          <p class="text-gray-800 leading-relaxed">
            I am a dedicated and versatile cook with over 5 years of experience in dynamic and high-volume catering environments.
            From premium banquets to large festivals, I have contributed to diverse operations with professionalism and adaptability.
            Through my hands-on involvement in logistics, service, and customer interaction, I’ve developed a wide understanding of kitchen and event operations.
            This has made me a highly flexible team member with a broad, strategic view of the hospitality industry.
          </p>
        </section>

        <!-- Experience -->
        <section>
          <h2 class="text-xl font-semibold text-gray-700 mb-2">Work Experience</h2>

          <!-- Choux de Bruxelles -->
          <div class="mb-4">
            <h3 class="font-bold text-gray-800">Choux de Bruxelles</h3>
            <p class="italic text-sm text-gray-600">2019 – 2021 – Kitchen Assistant</p>
            <ul class="list-disc list-inside text-gray-800 mt-2 space-y-1">
              <li>Prepared mise en place and assisted with hot and cold stations.</li>
              <li>Supported chefs during high-end banquets, weddings, and receptions.</li>
              <li>Maintained hygiene and food safety compliance (HACCP).</li>
              <li>Provided backup for dishwashing and kitchen cleaning when needed.</li>
            </ul>
          </div>

          <!-- Outré -->
          <div class="mb-4">
            <h3 class="font-bold text-gray-800">Outré NV (Belgium)</h3>
            <p class="italic text-sm text-gray-600">2021 – 2022 – Assistant Cook (Catering)</p>
            <ul class="list-disc list-inside text-gray-800 mt-2 space-y-1">
              <li>Assisted in preparation and execution of large-scale events (up to 1,500 guests).</li>
              <li>Handled various food stations and supported setup/teardown operations.</li>
              <li>Adapted to different event formats including formal dinners and outdoor festivals.</li>
              <li>Maintained flexibility and teamwork under pressure in mobile kitchen setups.</li>
            </ul>
          </div>

          <!-- Ethnic Food -->
          <div>
            <h3 class="font-bold text-gray-800">Ethnic Food – Catering Services</h3>
            <p class="italic text-sm text-gray-600">2022 – 2025 – Assistant Cook & Team Lead</p>
            <ul class="list-disc list-inside text-gray-800 mt-2 space-y-1">
              <li>Delivered catering services for diverse events across Belgium.</li>
              <li>Oversaw service teams and coordinated on-site logistics.</li>
              <li>Maintained direct communication with clients and ensured service satisfaction.</li>
              <li>Adapted menus and operations to match cultural and event-specific needs.</li>
              <li>Acted as both hands-on cook and front-line representative of the brand.</li>
            </ul>
          </div>
        </section>

        <!-- Skills -->
        <section>
          <h2 class="text-xl font-semibold text-gray-700 mb-2">Skills</h2>
          <ul class="grid grid-cols-2 gap-x-4 gap-y-1 text-gray-800 list-disc list-inside">
            <li>Team collaboration</li>
            <li>Time management</li>
            <li>Adaptability & versatility</li>
            <li>Food safety (HACCP)</li>
            <li>Stress resilience</li>
            <li>Client-facing communication</li>
            <li>Service coordination</li>
            <li>Event logistics</li>
          </ul>
        </section>

        <!-- Languages -->
        <section>
          <h2 class="text-xl font-semibold text-gray-700 mb-2">Languages</h2>
          <p class="text-gray-800">French (native), English (C1), German (A1)</p>
        </section>

        <!-- Certifications -->
        <section>
          <h2 class="text-xl font-semibold text-gray-700 mb-2">Education & Certifications</h2>
          <ul class="list-disc list-inside text-gray-800">
            <li>High School Diploma</li>
            <li>Certificate in Accounting</li>
          </ul>
        </section>
      </div>
    </section>
  </main>
</template>

<script setup>
const phone = '01628053880'
const email = 'karimbouziane29@gmail.com'
</script>

<style>
body {
  margin: 0;
  font-family: 'Inter', sans-serif;
}
</style>

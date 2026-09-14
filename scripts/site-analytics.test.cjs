const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const code = readFileSync(join(__dirname, '..', 'site.js'), 'utf8');
const consentKey = 'arij_maths_analytics_consent';
const pendingKey = 'arij_maths_pending_enquiry_v2';
const sourceKey = 'arij_maths_enquiry_source';
const nextUrl = 'https://maths.arijasad.com/thank-you.html';
const baseTime = 1790000000000;
let randomSequence = 0;

function browser(options = {}) {
  const session = options.session || new Map();
  const local = options.local || new Map(options.consent ? [[consentKey, options.consent]] : []);
  let clock = options.now || baseTime;
  const storage = (map, fail) => ({
    getItem(key) { if (fail) throw Error('Storage unavailable'); return map.has(key) ? map.get(key) : null; },
    setItem(key, value) { if (fail) throw Error('Storage unavailable'); map.set(key, String(value)); },
    removeItem(key) { if (fail) throw Error('Storage unavailable'); map.delete(key); }
  });
  const listeners = new Map();
  const documentListeners = new Map();
  const children = [];
  function element(tag = '') {
    return {
      tag, dataset: {}, className: '', value: '', textContent: '', listeners: new Map(), fields: new Map(),
      addEventListener(type, fn) { this.listeners.set(type, fn); },
      setAttribute() {}, focus() {},
      querySelector(selector) { if (!this.fields.has(selector)) this.fields.set(selector, element()); return this.fields.get(selector); },
      remove() { const index = children.indexOf(this); if (index !== -1) children.splice(index, 1); },
      click() { this.listeners.get('click')?.({ target: this }); }
    };
  }
  const next = element(); next.value = nextUrl;
  const honey = element(); honey.value = options.honey || '';
  const form = element('form');
  form.checkValidity = () => options.valid !== false;
  form.fields.set('[name="_next"]', next); form.fields.set('[name="_honey"]', honey);
  const heading = element(); const message = element();
  const settings = element();
  const resourceLink = element('a'); resourceLink.href = 'https://maths.arijasad.com/contact.html?service=TMUA#enquiry-form';
  const mailLink = element('a'); mailLink.href = 'mailto:arijasadmaths@gmail.com?subject=Private%20student%20details';
  const location = new URL(options.url || 'https://maths.arijasad.com/contact.html');
  const document = {
    cookie: '', documentElement: { lang: 'en-GB' },
    body: { hasAttribute: (name) => name === 'data-enquiry-confirmation' && location.pathname === '/thank-you.html', appendChild: (item) => children.push(item) },
    head: { appendChild: (item) => children.push(item) }, createElement: element,
    addEventListener: (type, fn) => documentListeners.set(type, fn),
    querySelector(selector) {
      if (selector === '#enquiry-form-fields') return options.form === false ? null : form;
      if (selector === '[data-enquiry-heading]') return heading;
      if (selector === '[data-enquiry-message]') return message;
      if (selector === '.cookie-banner') return children.find((item) => item.className === 'cookie-banner') || null;
      if (selector === 'script[data-arij-analytics]') return children.find((item) => item.dataset.arijAnalytics) || null;
      return null;
    },
    querySelectorAll(selector) {
      if (selector === '[data-cookie-settings]') return [settings];
      if (selector === 'a[href^="mailto:"]') return [mailLink];
      if (selector === 'a[href]') return [resourceLink, mailLink];
      return [];
    }
  };
  const window = {
    location, history: { state: null, replaceState(_state, _title, href) { if (options.historyFails) throw Error('Unavailable'); location.href = href; } },
    localStorage: storage(local, options.localFails), sessionStorage: storage(session, options.storageFails),
    crypto: { getRandomValues(bytes) { if (options.cryptoFails) throw Error('Unavailable'); bytes.fill(++randomSequence); return bytes; } },
    addEventListener: (type, fn) => listeners.set(type, fn)
  };
  class ClockDate extends Date { constructor(...args) { super(...(args.length ? args : [clock])); } static now() { return clock; } }
  vm.runInNewContext(code, { window, document, URL, URLSearchParams, Date: ClockDate, Uint8Array, navigator: {} });
  return {
    window, session, local, document, heading, message, next, resourceLink, mailLink,
    events: (name) => (window.dataLayer || []).map((args) => [...args]).filter((args) => args[0] === 'event' && args[1] === name),
    commands: () => (window.dataLayer || []).map((args) => [...args]),
    scripts: () => children.filter((item) => item.dataset.arijAnalytics),
    submit: (defaultPrevented = false) => documentListeners.get('submit')?.({ target: form, defaultPrevented }),
    choose(value) { settings.click(); document.querySelector('.cookie-banner').querySelector(`[data-cookie-${value}]`).click(); },
    storageChange(value) { if (value === null) local.clear(); else local.set(consentKey, value); listeners.get('storage')({ key: value === null ? null : consentKey }); },
    advance(ms) { clock += ms; }
  };
}
function submitAndReturn(options = {}, returnOptions = {}) {
  const source = browser(options); source.submit();
  const returned = browser({ session: source.session, local: source.local, url: source.next.value, ...returnOptions });
  return { source, returned };
}

test('analytics loads only after a positive consent choice', () => {
  const b = browser(); assert.equal(b.scripts().length, 0);
  b.choose('accept'); assert.equal(b.scripts().length, 1);
  b.choose('reject'); assert.equal(b.scripts().length, 0);
});
test('a direct or bookmarked thank-you visit never creates a lead', () => {
  const b = browser({ consent: 'accepted', url: nextUrl });
  assert.equal(b.events('generate_lead').length, 0);
});
test('native submission adds a random reference containing no form data', () => {
  const b = browser({ consent: 'accepted' }); b.submit();
  const token = new URL(b.next.value).searchParams.get('enquiry_return');
  assert.match(token, /^[a-f0-9]{32}$/);
  const record = JSON.parse(b.session.get(pendingKey));
  assert.deepEqual(Object.keys(record).sort(), ['analyticsEligible', 'createdAt', 'id']);
  assert.equal(b.events('generate_lead').length, 0);
});
test('a matched provider return is counted once and its reference is absent from analytics', () => {
  const { source, returned } = submitAndReturn({ consent: 'accepted' });
  assert.equal(returned.events('generate_lead').length, 1);
  assert.equal(returned.window.location.href, nextUrl);
  assert.equal(returned.session.has(pendingKey), false);
  assert.match(returned.heading.textContent, /submitted/);
  assert.equal(JSON.stringify(returned.commands()).includes('enquiry_return'), false);
  assert.equal(JSON.stringify(returned.commands()).includes(new URL(source.next.value).searchParams.get('enquiry_return')), false);
  const reload = browser({ consent: 'accepted', session: returned.session, url: source.next.value });
  assert.equal(reload.events('generate_lead').length, 0);
});
test('expired and mismatched returns are not conversions', () => {
  const expired = submitAndReturn({ consent: 'accepted' }, { now: baseTime + 15 * 60 * 1000 });
  assert.equal(expired.returned.events('generate_lead').length, 0);
  const source = browser({ consent: 'accepted' }); source.submit();
  const mismatch = browser({ consent: 'accepted', session: source.session, url: nextUrl + '?enquiry_return=' + 'f'.repeat(32) });
  assert.equal(mismatch.events('generate_lead').length, 0);
});
test('unavailable storage and crypto preserve the ordinary native form return', () => {
  for (const fault of ['storageFails', 'cryptoFails']) {
    const b = browser({ consent: 'accepted', [fault]: true }); b.submit();
    assert.equal(b.next.value, nextUrl);
    assert.equal(b.events('generate_lead').length, 0);
  }
});
test('cancelled, invalid and honeypot submissions cannot create pending conversions', () => {
  for (const options of [{}, { valid: false }, { honey: 'bot' }]) {
    const b = browser({ consent: 'accepted', ...options }); b.submit(Object.keys(options).length === 0);
    assert.equal(b.session.has(pendingKey), false);
    assert.equal(b.next.value, nextUrl);
  }
});
test('a valid return can count after consent is first accepted on that page', () => {
  const { returned } = submitAndReturn();
  assert.equal(returned.events('generate_lead').length, 0);
  returned.choose('accept'); assert.equal(returned.events('generate_lead').length, 1);
  returned.choose('accept'); assert.equal(returned.events('generate_lead').length, 1);
});
test('a delayed first acceptance cannot count an expired return', () => {
  const { returned } = submitAndReturn(); returned.advance(15 * 60 * 1000);
  returned.choose('accept'); assert.equal(returned.events('generate_lead').length, 0);
});
test('rejecting a return clears it permanently even if consent is later accepted', () => {
  const { returned } = submitAndReturn(); returned.choose('reject'); returned.choose('accept');
  assert.equal(returned.events('generate_lead').length, 0);
  const updates = returned.commands().filter((args) => args[0] === 'consent' && args[1] === 'update');
  assert.equal(updates.at(-1)[2].analytics_storage, 'granted');
});
test('a submission made while consent is rejected is never backfilled', () => {
  const { returned } = submitAndReturn({ consent: 'rejected' }, { local: new Map([[consentKey, 'accepted']]) });
  assert.equal(returned.events('generate_lead').length, 0);
  assert.match(returned.heading.textContent, /submitted/);
});
test('withdrawal in another tab stops clicks and clears pending attribution', () => {
  const b = browser({ consent: 'accepted', url: 'https://maths.arijasad.com/resources.html' });
  b.resourceLink.click(); b.submit();
  assert.ok(b.session.has(pendingKey));
  b.storageChange('rejected'); b.mailLink.click(); b.resourceLink.click();
  assert.equal(b.session.has(pendingKey), false); assert.equal(b.session.has(sourceKey), false);
  assert.equal(b.events('contact_click').length, 0); assert.equal(b.events('resource_enquiry_click').length, 1);
  assert.equal(b.scripts().length, 0);
});
test('clearing consent in another tab also invalidates an uncounted return', () => {
  const { returned } = submitAndReturn(); returned.storageChange(null); returned.choose('accept');
  assert.equal(returned.events('generate_lead').length, 0);
});
test('resource clicks use known paths only and do not include contact query strings', () => {
  for (const path of ['/resources.html', '/algebra-to-tmua-diagnostic.html', '/teaching-practice-sequences.html']) {
    const b = browser({ consent: 'accepted', url: 'https://maths.arijasad.com' + path }); b.resourceLink.click();
    assert.equal(b.events('resource_enquiry_click').length, 1);
    assert.equal(b.events('resource_enquiry_click')[0][2].resource_source, path);
    assert.equal(JSON.stringify(b.commands()).includes('service='), false);
  }
  const unknown = browser({ consent: 'accepted', url: 'https://maths.arijasad.com/unknown.html' }); unknown.resourceLink.click();
  assert.equal(unknown.events('resource_enquiry_click').length, 0);
});
test('fresh approved resource attribution survives a form return; expired or arbitrary paths do not', () => {
  for (const [path, age, included] of [['/resources.html', 0, true], ['/resources.html', 900000, false], ['/private-student.html', 0, false]]) {
    const session = new Map([[sourceKey, JSON.stringify({ path, createdAt: baseTime - age })]]);
    const { returned } = submitAndReturn({ consent: 'accepted', session });
    assert.equal(returned.events('generate_lead')[0][2].resource_source, included ? path : undefined);
  }
});
test('each fresh form submission in the same browser session can count separately', () => {
  const first = submitAndReturn({ consent: 'accepted' });
  const second = submitAndReturn({ consent: 'accepted', session: first.returned.session });
  assert.notEqual(first.source.next.value, second.source.next.value);
  assert.equal(first.returned.events('generate_lead').length, 1);
  assert.equal(second.returned.events('generate_lead').length, 1);
});
test('mailto measurement requires current consent and strips the message query', () => {
  const b = browser({ consent: 'accepted' }); b.mailLink.click();
  assert.equal(b.events('contact_click')[0][2].link_url, 'mailto:arijasadmaths@gmail.com');
  b.choose('reject'); b.mailLink.click(); assert.equal(b.events('contact_click').length, 1);
});
test('GA configuration still gets a clean URL if browser history replacement fails', () => {
  const { returned } = submitAndReturn({ consent: 'accepted' }, { historyFails: true });
  const config = returned.commands().find((args) => args[0] === 'config');
  assert.equal(config[2].page_location, nextUrl);
  assert.equal(JSON.stringify(returned.commands()).includes('enquiry_return'), false);
});

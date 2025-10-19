import assert from 'assert';
import { render } from '@testing-library/preact';
import Header from '../components/Header.astro';

describe('Header', () => {
  it('renders the header', () => {
    const { container } = render(Header);
    assert.ok(container.querySelector('header'));
  });
});

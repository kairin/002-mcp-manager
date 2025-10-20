/**
 * Module Independence Integration Tests
 * 
 * Purpose: Verify that TUI, CI/CD, and Website modules are truly independent
 * per FR-006 (Modular Implementation) requirement.
 * 
 * Test Strategy:
 * 1. TUI changes don't affect CI/CD or Website
 * 2. CI/CD changes don't affect Website or TUI
 * 3. Website changes don't affect TUI or CI/CD
 * 
 * Feature: 001-local-cicd-astro-site
 * Tasks: T070-T071
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

describe('Module Independence Tests (FR-006)', () => {
  const PROJECT_ROOT = path.resolve(__dirname, '../../../');
  const TUI_DIR = path.join(PROJECT_ROOT, 'scripts/tui');
  const CI_DIR = path.join(PROJECT_ROOT, 'scripts/local-ci');
  const WEB_DIR = path.join(PROJECT_ROOT, 'web');

  describe('Module Existence', () => {
    it('should have separate TUI module directory', () => {
      expect(fs.existsSync(TUI_DIR)).toBe(true);
      expect(fs.existsSync(path.join(TUI_DIR, 'run.sh'))).toBe(true);
    });

    it('should have separate CI/CD module directory', () => {
      expect(fs.existsSync(CI_DIR)).toBe(true);
      expect(fs.existsSync(path.join(CI_DIR, 'run.sh'))).toBe(true);
    });

    it('should have separate Website module directory', () => {
      expect(fs.existsSync(WEB_DIR)).toBe(true);
      expect(fs.existsSync(path.join(WEB_DIR, 'package.json'))).toBe(true);
    });
  });

  describe('TUI Module Independence', () => {
    it('TUI should not import or require CI/CD implementation details', () => {
      const tuiScript = fs.readFileSync(path.join(TUI_DIR, 'run.sh'), 'utf8');
      
      // TUI should call CI/CD script as black box, not source it
      expect(tuiScript).not.toContain('source.*local-ci.*run.sh');
      expect(tuiScript).not.toContain('. .*local-ci.*run.sh');
      
      // TUI should execute CI/CD script, not embed its logic
      expect(tuiScript).toContain('$CI_SCRIPT');
    });

    it('TUI should not directly manipulate website files', () => {
      const tuiScript = fs.readFileSync(path.join(TUI_DIR, 'run.sh'), 'utf8');
      
      // TUI should not touch web/ directory
      expect(tuiScript).not.toContain('cd.*web');
      expect(tuiScript).not.toContain('npm run');
      expect(tuiScript).not.toContain('astro');
    });

    it('TUI documentation should exist independently', () => {
      const tuiReadme = path.join(TUI_DIR, 'README.md');
      expect(fs.existsSync(tuiReadme)).toBe(true);
      
      const content = fs.readFileSync(tuiReadme, 'utf8');
      expect(content).toContain('TUI');
      expect(content).toContain('Menu');
    });
  });

  describe('CI/CD Module Independence', () => {
    it('CI/CD should not know about TUI implementation', () => {
      const ciScript = fs.readFileSync(path.join(CI_DIR, 'run.sh'), 'utf8');
      
      // CI/CD should not reference TUI
      expect(ciScript).not.toContain('tui');
      expect(ciScript).not.toContain('menu');
      expect(ciScript).not.toContain('interactive');
    });

    it('CI/CD should work standalone via CLI flags', () => {
      const ciScript = fs.readFileSync(path.join(CI_DIR, 'run.sh'), 'utf8');
      
      // CI/CD should accept CLI arguments
      expect(ciScript).toContain('--help');
      expect(ciScript).toContain('--verbose');
      expect(ciScript).toContain('--skip-tests');
      expect(ciScript).toContain('--no-fix');
    });

    it('CI/CD libraries should be modular and reusable', () => {
      const libDir = path.join(CI_DIR, 'lib');
      expect(fs.existsSync(libDir)).toBe(true);
      
      const logger = path.join(libDir, 'logger.sh');
      const validator = path.join(libDir, 'validator.sh');
      
      expect(fs.existsSync(logger)).toBe(true);
      expect(fs.existsSync(validator)).toBe(true);
    });
  });

  describe('Website Module Independence', () => {
    it('Website should not reference TUI or CI/CD scripts', () => {
      const packageJson = JSON.parse(
        fs.readFileSync(path.join(WEB_DIR, 'package.json'), 'utf8')
      );
      
      // Website scripts should not call TUI or CI/CD
      const scripts = JSON.stringify(packageJson.scripts || {});
      expect(scripts).not.toContain('../scripts/tui');
      expect(scripts).not.toContain('../scripts/local-ci');
    });

    it('Website should be buildable independently', () => {
      const packageJson = JSON.parse(
        fs.readFileSync(path.join(WEB_DIR, 'package.json'), 'utf8')
      );
      
      // Website must have its own build script
      expect(packageJson.scripts).toHaveProperty('build');
      expect(packageJson.scripts).toHaveProperty('dev');
    });

    it('Website tests should not depend on CI/CD internals', () => {
      const testFiles = fs.readdirSync(path.join(WEB_DIR, 'tests/unit'));
      
      // Unit tests should exist
      expect(testFiles.length).toBeGreaterThan(0);
      
      // Tests should not import CI/CD modules
      testFiles.forEach(file => {
        if (file.endsWith('.test.js')) {
          const content = fs.readFileSync(
            path.join(WEB_DIR, 'tests/unit', file),
            'utf8'
          );
          expect(content).not.toContain('../../scripts/local-ci');
          expect(content).not.toContain('../../scripts/tui');
        }
      });
    });
  });

  describe('Module Boundary Enforcement', () => {
    it('each module should have its own README', () => {
      expect(fs.existsSync(path.join(TUI_DIR, 'README.md'))).toBe(true);
      expect(fs.existsSync(path.join(CI_DIR, 'README.md'))).toBe(true);
      expect(fs.existsSync(path.join(WEB_DIR, 'README.md'))).toBe(true);
    });

    it('modules should communicate via documented interfaces only', () => {
      // TUI calls CI/CD via command-line interface
      const tuiScript = fs.readFileSync(path.join(TUI_DIR, 'run.sh'), 'utf8');
      expect(tuiScript).toMatch(/\$CI_SCRIPT\s+--/); // CLI flags
      
      // CI/CD outputs structured logs (JSON)
      const ciScript = fs.readFileSync(path.join(CI_DIR, 'run.sh'), 'utf8');
      expect(ciScript).toContain('log_json');
      expect(ciScript).toContain('jq');
    });

    it('no circular dependencies between modules', () => {
      const tuiScript = fs.readFileSync(path.join(TUI_DIR, 'run.sh'), 'utf8');
      const ciScript = fs.readFileSync(path.join(CI_DIR, 'run.sh'), 'utf8');
      
      // TUI can call CI/CD
      expect(tuiScript).toContain('CI_SCRIPT');
      
      // But CI/CD should NOT call TUI back
      expect(ciScript).not.toContain('tui/run.sh');
      expect(ciScript).not.toContain('../tui');
    });
  });

  describe('Independent Testability', () => {
    it('TUI should be testable without running CI/CD', () => {
      // TUI functions should be defined and callable
      const tuiScript = fs.readFileSync(path.join(TUI_DIR, 'run.sh'), 'utf8');
      
      expect(tuiScript).toContain('main_menu()');
      expect(tuiScript).toContain('show_help()');
      expect(tuiScript).toContain('check_environment()');
    });

    it('CI/CD should be testable without TUI or website', () => {
      // CI/CD should have standalone test capability
      const libTestScript = path.join(CI_DIR, 'lib/logger.test.sh');
      
      // Logger has its own tests
      if (fs.existsSync(libTestScript)) {
        const content = fs.readFileSync(libTestScript, 'utf8');
        expect(content).toContain('test');
      }
    });

    it('Website should be testable without CI/CD scripts', () => {
      const packageJson = JSON.parse(
        fs.readFileSync(path.join(WEB_DIR, 'package.json'), 'utf8')
      );
      
      // Website has its own test command
      expect(packageJson.scripts).toHaveProperty('test');
    });
  });
});

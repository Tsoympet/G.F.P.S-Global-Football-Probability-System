import '@testing-library/jest-dom';
import { webcrypto } from 'crypto';

if (!(global as any).crypto) {
  (global as any).crypto = webcrypto as unknown as Crypto;
}

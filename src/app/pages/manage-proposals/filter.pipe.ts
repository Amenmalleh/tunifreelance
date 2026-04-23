import { Pipe, PipeTransform } from '@angular/core';
import { Proposal } from '../../services/proposal.service';

@Pipe({
  name: 'filter',
  standalone: true
})
export class FilterPipe implements PipeTransform {
  transform(proposals: Proposal[], status: string): Proposal[] {
    if (!proposals || !status) {
      return proposals;
    }
    return proposals.filter(p => p.status === status);
  }
}
